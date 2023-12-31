# Yällo!
#### Video Demo: https://youtu.be/N6QyHvpMC0k
#### Description: A code sharing solution that allows users to share and request code with a clean and intuitive look
#### Currently now live at: https://gravitationally.online

### Share code solutions with other programmers
It is a code sharing solution where other programmers can ask other programmers for solutions or share what their solutions are on regular problems like a binary sort for example. It can be a safe environment with the report feature and you can like and reply to any Post allowing for frequent discussions. You can also search up everything in the search tab allowing you to look up a variety of things. I made this because I felt that this website idea needed some more innovation and variety, so I tried making my own mix into things and trying it out!
### How its structured
#### Frontend
Using Bootstrap, the ace c9 editor and some javascript elbow grease. I was able to make a reliable application that looks sleek and fine to use and communicate with. It uses the APIs made in the backend to show all items safely, and I also chose a flex box as the main way of showing posts since it seems free flowing and nice to look around in
#### Backend
Using flask and many python utilities i was able to make a secure applications and apis to allow the front end to run as smoothly as possible, including pygment to highlight code blocks, and nh3(ammonia) to santize text, the apis are nicely secure with many checks, a
#### Database
Uses SQLAlchemy
A Yell (post, request or comments) are located in a single table which it has all the attributes to titles to likes and others, there are 3 other tables named posts, requests and comments that take Yell as a foregin key to inherit its properties from and each one now also has extra info like what filename it is.
The comments are collected which has a foreign key pointed to a Comment Set which comment set is pointed to a Yell, but that Comments are also Yells, so you could theoretically have an indefinite loop of going from comments to comment sets to comments agains which makes it very nice
##### Message
This was made in like 2-3 weeks by myself throughout Christmas and I'm very tired

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

> if it doesnt work, try running the exports that are at the end of the file in setup.sh
