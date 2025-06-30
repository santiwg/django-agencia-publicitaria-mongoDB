FROM python:3.10-alpine AS base
LABEL maintainer="Santiago Wursten Gill <santiwgwuri@gmail.com>, Imanol Barrionuevo <barrionuevoimanol@gmail.com>"
LABEL version="1.0"
LABEL description="cloudset"
RUN apk --no-cache add bash pango ttf-freefont py3-pip curl

FROM base AS builder
RUN apk --no-cache add py3-pip py3-pillow py3-brotli py3-scipy py3-cffi \
  linux-headers autoconf automake libtool gcc cmake python3-dev \
  fortify-headers binutils libffi-dev wget openssl-dev libc-dev \
  g++ make musl-dev pkgconf libpng-dev openblas-dev build-base \
  font-noto terminus-font libffi

COPY ./requirements.txt .
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && rm requirements.txt

FROM base
RUN mkdir /code
WORKDIR /code
COPY ./requirements.txt .
RUN pip install -r requirements.txt \
  && rm requirements.txt

# Copia tanto los paquetes de Python como los binarios instalados (¡IMPORTANTE!)
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Asegúrate de que el PATH incluya /usr/local/bin/
ENV PATH="/usr/local/bin:${PATH}"

RUN ln -s /usr/share/zoneinfo/America/Cordoba /etc/localtime
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "app.wsgi"]
