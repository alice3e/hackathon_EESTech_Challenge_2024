FROM public.ecr.aws/lambda/python:3.8

RUN pip install pipenv

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY model_C=1.0.bin .

COPY lambda_function.py .

CMD ["lambda_function.lambda_handler"]