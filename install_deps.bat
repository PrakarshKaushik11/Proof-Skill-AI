@echo off
REM Install missing dependencies
cd /d "D:\Deviathon 2.0\ProofSkillAI"
call .venv\Scripts\activate.bat

echo Installing missing dependencies...
pip install "thinc<8.4.0,>=8.3.12" click jinja2 requests tqdm filelock fsspec certifi tabulate websockets httpx python-dateutil tzdata

echo.
echo Installing additional streamlit dependencies...
pip install protobuf pydeck altair click pillow protobuf pyarrow starlette uvicorn anyio python-multipart itsdangerous watchdog websockets sympy networkx jinja2 filelock fsspec certifi tabulate websockets httpx python-dateutil tzdata

echo.
echo Installing missing gradio/huggingface dependencies...
pip install fsspec httpx websockets requests pyjwt pynacl lxml

echo.
echo Installing spacy dependencies...
pip install click<9.0.0,>=8.2.1 jinja2 requests<3.0.0,>=2.13.0 tqdm typer<1.0.0,>=0.3.0 weasel click<9,>=7.0 pillow<14,>=9.2.0 protobuf<8,>=5.26.1 pyarrow!=25.0.0,<27,>=10.0.1 pydeck<1,>=0.8.0b4 altair!=5.4.0,!=5.4.1,<7,>=5.0.0 starlette<2,>=0.46.0 uvicorn<1,>=0.30.0 anyio<5,>=4.0.0 python-multipart<1,>=0.0.10 itsdangerous<3,>=2.1.2 watchdog<7,>=2.1.5 websockets<18,>=12.0.0

echo.
echo All dependencies installed!
pause