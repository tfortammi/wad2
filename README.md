![GIF demo](readme/header.gif)

# ProjectQuest

Problem identified: During the pandemic, many companies have been forced to adopt flexible and remote working arrangements. To improve motivation among the employees, our project aims to bring RPG elements into a work productivity application specifically for Software Developers. 

Our solution: A gamified Software Project Management tool for easy remote team and task management.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the following libraries.

```bash
pip install flask
pip install flask_sqlalchemy
pip install flask_cors
pip install firebase_admin
```
We have included a `readme/requirements.txt` file that you can use to recursively install the necessary python libraries.

## Usage
In order to run the Web Application, first start running the `api/main.py` file 

If you are using Windows OS, you may use the following commands:
```bash
cd api/
python main.py
```

If you are using Machintosh OS, you may use the following commands:
```bash
cd api/
python main.py
```

To visit the Web Application, simply locate the folder where you've downloaded the file and add `/app` to the back of the link. For e.g. `file:///Applications/MAMP/htdocs/wad2/app`

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

**Acknowledgements**
---

+ [@shobrook](https://www.github.com/shobrook) for logo and UI design assistance.
+ Base logo vector made by [Freepik](https://www.freepik.com/) from [Flaticon](www.flaticon.com).
+ [drduh's macOS-Security-and-Privacy-Guide](https://github.com/drduh/macOS-Security-and-Privacy-Guide) and [Jonathan Levin's MacOS Security Guide](http://newosxbook.com/files/moxii3/AppendixA.pdf) were incredibly helpful while I was building `stronghold`.

## License
[MIT](https://choosealicense.com/licenses/mit/)
