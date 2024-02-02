from setuptools import setup

if __name__ == "__main__":
    try:
        setup(
            version="1.0.3",  # Set the desired version here
            use_scm_version={"version_scheme": "no-guess-dev"},
        )
    except Exception as e:
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm, and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise e
