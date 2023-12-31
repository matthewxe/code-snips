# Yällo!
#### Video Demo:
#### A code sharing solution that allows users to share and request code with a clean and intuitive look
#### Currently now live at: https://gravitationally.online

###
share snippets of code with other people
### How its structured
#### Frontend
Using Bootstrap, the ace c9 editor and some javascript elbow grease. I was able to make a reliable application that looks sleek and fine to use and communicate with.
#### Backend
Using flask and many python utilities i was able to make a secure applications and apis to allow the front end to run as smoothly as possible, including pygment to highlight code blocks, and nh3(ammonia) to santize text
#### Database
Uses SQLAlchemy
and Posts, Requests and Comments all hail from a single table which then each type will have its own table havinf the original table as a foreign key,

#### how to deploy on your own

1. Create new venv

```bash
python -m venv ./venv
source ./venv/bin/activate
```

2. Run setup

```bash
./setup.sh
```

3. Deploy

```bash
./deploy.sh
```

> if it doesnt work, try running the exports that are at th =e end of the file in setup.sh

## Powered by

- [Bootstrap](https://getbootstrap.com)
- [Prismjs](https://prismjs.com)
- [Ace](https://ace.c9.io/)
