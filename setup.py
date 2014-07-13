from setuptools import setup

setup(name='xapian_case',
      version='0.1',
      url='https://github.com/linhaobuaa/xapian_case',
      author='linhaobuaa',
      packages=['xapian_case'],
      data_files=[('dict', ['dict/userdic.txt', 'dict/stopword.txt', 'dict/emotionlist.txt', 'dict/one_word_white_list.txt'])],
      install_requires=[
          'pyzmq',
      ],
      dependency_links=[
      ],
)

# extra requires
# xapian and python-binding
# git@github.com:MOON-CLJ/pyscws.git
