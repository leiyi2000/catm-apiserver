FROM python:3.11-slim-bullseye as requirements-stage

WORKDIR /tmp

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install pdm
RUN pdm config pypi.url https://pypi.tuna.tsinghua.edu.cn/simple

COPY ./pyproject.toml ./pdm.lock* /tmp/
RUN pdm export -f requirements --output requirements.txt --without-hashes


FROM python:3.11-slim-bullseye

WORKDIR /code

# 拷贝requirements.txt
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
# 安装依赖
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./catm /code/catm
# COPY ./migrations /code/migrations
CMD ["uvicorn", "catm.main:app", "--host", "0.0.0.0", "--port", "8000"]