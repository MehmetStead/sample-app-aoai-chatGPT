FROM node:20-alpine AS frontend  
RUN mkdir -p /home/node/app/node_modules && chown -R node:node /home/node/app

WORKDIR /home/node/app 
COPY ./frontend/package*.json ./  
USER node
RUN npm ci  
COPY --chown=node:node ./frontend/ ./frontend  
COPY --chown=node:node ./static/ ./static  
WORKDIR /home/node/app/frontend
RUN NODE_OPTIONS=--max_old_space_size=8192 npm run build
  
FROM python:3.11-alpine 
RUN apk add --no-cache --virtual .build-deps \  
    build-base \  
    libffi-dev \  
    openssl-dev \  
    curl \  
    rust \
    cargo \
    && apk add --no-cache \  
    libpq 
  
COPY requirements.txt /usr/src/app/  
# First upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \
    # Then try to install requirements with pre-built wheels
    pip install --no-cache-dir --prefer-binary -r /usr/src/app/requirements.txt && \
    rm -rf /root/.cache  
  
COPY . /usr/src/app/  
COPY --from=frontend /home/node/app/static  /usr/src/app/static/

# Copy env files
COPY .env /usr/src/app/.env
COPY .env.development /usr/src/app/.env.development

WORKDIR /usr/src/app  
EXPOSE 80  

CMD ["sh", "-c", "PYTHONUNBUFFERED=1 gunicorn -b 0.0.0.0:80 -w 4 --log-level=info --capture-output --log-file=- app:app"]