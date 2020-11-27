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
)
