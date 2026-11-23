# Headless JoyCaption batch captioner for Runpod Serverless.
# No model weights are baked in: Beta One (~15.8 GiB) is downloaded at job start
# and cached on the network volume (/runpod-volume/joycaption/models) when one
# is attached.
#
# Official code has no tags; pin the SHA below. This SHA is only the Docker pin;
# our GitHub release for the Hub must use targetCommitish=main.
ARG BASE_IMAGE=nvidia/cuda:12.8.1-cudnn-runtime-ubuntu24.04
FROM ${BASE_IMAGE}

ARG JOYCAPTION_SHA=8445b2e55db7856d522e44ae84e7415fcf3413f6

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    HF_HUB_ENABLE_HF_TRANSFER=1 \
    HF_HUB_DISABLE_TELEMETRY=1 \
    TOKENIZERS_PARALLELISM=false \
    JOYCAPTION_DIR=/opt/joycaption \
    MODEL_ID=fancyfeast/llama-joycaption-beta-one-hf-llava \
    MODEL_REVISION=ebf414ea497a020da0f82df3913e5b6cb8e9663a

# git: clone upstream; ffmpeg: exotic image containers; python3.12 is Ubuntu 24.04 default.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git ffmpeg ca-certificates \
        python3 python3-venv python3-pip python3-dev \
    && ln -sf /usr/bin/python3 /usr/local/bin/python \
    && rm -rf /var/lib/apt/lists/* \
    && python -c "import sys; assert sys.version_info[:2] == (3, 12), sys.version"

# Clone the official repo and check out the pinned SHA. Do not clone a floating main.
# Do not start the official GUI; ComfyUI and finetuning/ are unused at runtime. Drop .git after the pin.
RUN git clone https://github.com/fpgaminer/joycaption.git ${JOYCAPTION_DIR} \
    && cd ${JOYCAPTION_DIR} \
    && git checkout ${JOYCAPTION_SHA} \
    && git rev-parse HEAD > /opt/joycaption.commit \
    && test "$(cat /opt/joycaption.commit)" = "${JOYCAPTION_SHA}" \
    && rm -rf .git

# Use a venv so we do not fight the Debian pip install (no RECORD file).
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

# Stage 1: official torch 2.7.1+cu128 from download.pytorch.org (allowed stand-in for
# the upstream pin of torch==2.7.0). torchvision is required by batch-caption.py.
# Stage 2: official JoyCaption requirements (transformers 4.51.3, accelerate 1.6.0,
# pillow 11.2.1, triton 3.3.0). Do not upgrade transformers or torch after this.
WORKDIR ${JOYCAPTION_DIR}
RUN pip install --upgrade pip \
    && pip install torch==2.7.1+cu128 torchvision==0.22.1+cu128 torchaudio==2.7.1+cu128 \
        --index-url https://download.pytorch.org/whl/cu128 \
    && python -m pip freeze | grep -iE '^(torch|torchvision|torchaudio|triton|nvidia-[a-z0-9-]+)==' > /tmp/constraints.txt \
    && cat /tmp/constraints.txt \
    && python -m pip install \
        transformers==4.51.3 \
        accelerate==1.6.0 \
        pillow==11.2.1 \
        triton==3.3.0 \
        -c /tmp/constraints.txt \
    && python -m pip freeze | grep -iE '^(torch|torchvision|torchaudio|triton|nvidia-[a-z0-9-]+)==' > /tmp/constraints.txt

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN python -m pip install -r /app/requirements.txt -c /tmp/constraints.txt \
    && python -m pip freeze > /app/requirements.lock \
    && python -c "import sys,torch,torchvision,transformers,accelerate,PIL,runpod; print('torch', torch.__version__, '| cuda', torch.version.cuda, '| transformers', transformers.__version__, '| python', sys.version.split()[0], '| runpod', runpod.__version__, '| joycaption sha', open('/opt/joycaption.commit').read().strip())"

COPY handler.py /app/handler.py
COPY src /app/src

# No secrets are baked in: HF_TOKEN / BUCKET_* come from Runpod secrets at runtime.
# The official GUI is never started; the handler wraps official scripts/batch-caption.py.
WORKDIR /app
CMD ["python", "-u", "/app/handler.py"]
