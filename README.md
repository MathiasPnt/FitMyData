# FitMyData

## Access

The app is available online: https://share.streamlit.io/mathiaspnt/fitmydata/app.py

## Presentation

To cite this work, see [this file](./CITATION.cff).

The objective is to have a tool to quickly analyse data in the lab. It is not meant to cover all ppossibilities, but we would like this software to be as general as possible.

What has been implemented so far:
1. Lifetime for exciton (cosine with exp decay) and trion (exp decay)
2. HOM normalised by area of the side peaks
3. HOM normalised by uncorelated central peak (ortho/para)
4. g2
5. Reflectivity spectrum
6. photoluminescence spectrum
7. Pulse calculator


## Installation and running

### Docker

This is the preferred option since it doesn't require any already installed package on your device (except for Docker).

```bash
docker build -t fitmydata .
docker run -p 8501:8501 fitmydata
# Or you can rather use the following run command to mount your code into the docker so that you can change the code in your IDE and it will be sync into the docker
docker run -p 8501:8501 -v ~/FitMyData:/workspace fitmydata
```

and then open your browser to localhost:8501

### Without docker

If you're on Linux, you can directly do in your favorite shell:

```bash
apt update -y && xargs apt-get install -y <packages.txt
pip install -r requirements.txt
```


A C compiler is installed through `build-essential` in `packages.txt`. This is required to install the library `readPTU`.
On other platforms (Mac, Windows..) you will need to install for yourself a C compiler, this is why the docker option is simpler.

To run the streamlit app:

```bash
streamlit run app.py
```

## Contributing

To help me improve this toolbox + software:
**DO NOT PUSH OR COMMIT TO MAIN**.
You should rather:
1. Create a branch with your _FirstnameLastname for any modifications.
2. All push should be adding a reasonably small feature to only one of the files.
