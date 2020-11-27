import setuptools

setuptools.setup(
    name="camera",
    version="0.0.1",
    packages=["camera"],
    python_requires=">=3.7",
    install_requires=["picamera==1.13"],
    package_data={
        "camera": ["html/*.html"],
    },
    extras_require={"cv": ["opencv-python-headless==4.4.0.46", "tqdm==4.54.0"]},
)
