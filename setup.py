from distutils.core import setup

setup(
    name='tts_preprocessor',
    version='0.1',
    packages=['tts_preprocessor', 'tts_preprocessor.tests'],
    url='https://github.com/scholer/tts_preprocessor',
    license='GPLv3',
    author='Rasmus Scholer Sorensen',
    author_email='rasmusscholer@gmail.com',
    description='Optimize your text input for Text-To-Speech synthesis, '
                'stripping formatting (HTML, Latex, RTF) and replace abbreviations.',
    entry_points={
        'console_scripts': [
            # These should all be lower-case, else you may get an error when uninstalling:
            'tts_preprocessor=tts_preprocessor.common:main',
        ],
    },
    # pip will install these modules as requirements.
    install_requires=[
        'yaml',
    ],
)
