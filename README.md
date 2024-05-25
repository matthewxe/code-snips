# Yällo!
#### Video Demo: https://youtu.be/N6QyHvpMC0k
#### Description: A code sharing solution that allows users to share and request code with a clean and intuitive look
#### Currently now live at: https://gravitationally.online

### Share code solutions with other programmers
It is a code sharing solution where other programmers can ask other programmers for solutions or share what their solutions are on regular problems like a binary sort for example. It can be a safe environment with the report feature and you can like and reply to any Post allowing for frequent discussions. You can also search up everything in the search tab allowing you to look up a variety of things. I made this because I felt that this website idea needed some more innovation and variety, so I tried making my own mix into things and trying it out!
### How its structured
#### Frontend
This uses very basic [Bootstrap](https://getbootstrap.com/) as it's css framework.
The [Ace C9 Editor](https://ace.c9.io/) for the embedded editor because I don't think I can make anything remotely as complex as that.
I try making the buttons feel responsive by updating it using javascript and not fetching instead. 
I was able to make a reliable enough application that looks sleek and fine to use and communicate with.
I also chose a flex box as the main way of showing posts since it seems free flowing and nice to look around in.
#### Backend
This uses [Flask](https://flask.palletsprojects.com/en/3.0.x/) and many other python libraries.
The way you get information is simply just an api path where you can request a file id and thats it.
The other one is for searching, since you need to have constant updates I decided that it would be better that it could be a websocket, and as I never used this before I wanted to learn it, after implementing it works fairly smoothly.
##### Here are some of the python libraries that helped in the backend
1. [nh3](https://pypi.org/project/nh3/), adds python bindings to an html santizier named [rust-amonia](https://github.com/rust-ammonia/ammonia).
including pygment to highlight code blocks, and nh3(ammonia) to santize text, the apis are nicely secure with many checks, a
#### Database
Uses SQLAlchemy from within Flask
A Yell (post, request or comments) are located in a single table which it has all the attributes to titles to likes and others, there are 3 other tables named posts, requests and comments that take Yell as a foregin key to inherit its properties from and each one now also has extra info like what filename it is.
The comments are collected which has a foreign key pointed to a Comment Set which comment set is pointed to a Yell, but that Comments are also Yells, so you could theoretically have an indefinite loop of going from comments to comment sets to comments agains which makes it very nice
##### Message
This was made in like 2-3 weeks by myself throughout Christmas and I'm very tired
### The other stuff to credit
arstrast
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
