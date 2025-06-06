# Dwitter 🐦

Dwitter is a lightweight Twitter-like application built using Django, showcasing the speed and power of this incredible framework.

## Features 🚀

- ✅ User authentication (login & registration)
- 📝 Post tweets ("dweets") with up to 280 characters
- 📜 Global tweet feed
- 🔍 Search for tweets and users
- ➕ Follow/unfollow other users
- 👥 Explore user list
- 📊 View profile statistics: tweet count, likes, followers & following
- ❤️ Like tweets
- 🗑️ Delete your own tweets
- 🔄 Share button placeholder
- 👤 User profiles with avatar support (default placeholder if missing)
- 📷 Edit profile with drag & drop avatar upload
- ⚡ Fast dashboard thanks to [smart view-level caching](#-smart-caching)

## Screenshots 🖼️

### Login Page

![login](docs/login.png)

### Registration Page

![register](docs/register.png)

### Feed

![register](docs/feed.png)

### Users explore

![register](docs/explore.png)

### Edit profile

![register](docs/edit-profile.png)

### User details

![register](docs/user-details.png)

### Search results

![register](docs/search-results.png)

## Installation 🛠️

To run Dwitter locally:

```bash
git clone https://github.com/0x10-z/dwitter
cd dwitter

# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Migrate and run
python manage.py migrate
python manage.py runserver
```

Then visit [http://localhost:8000/](http://localhost:8000/) 🌍

## 🔑 Default Users (for testing)

> ⚠️ **For development purposes only**. Please change these credentials before deploying.

| Username   | Password    | Role        |
| ---------- | ----------- | ----------- |
| `admin`    | `admin1234` | Superuser   |
| `elonmusk` | `e12345678` | Normal user |

Make sure to change these credentials in production for security purposes.

## 🧠 Smart Caching

Dwitter now includes **view-level caching** to boost performance and reduce database load. When the same user requests the dashboard within a short period, the response is served from cache instead of querying the database again.

This results in much faster responses, as seen below:

```text
⚠️ Cache MISS
⏱ Dashboard view took: 0.0066 seconds
[31/May/2025 21:22:46] "GET / HTTP/1.1" 200 102078

✅ Cache HIT
⏱ Dashboard view took: 0.0020 seconds
[31/May/2025 21:22:47] "GET / HTTP/1.1" 200 102078

⚠️ Cache MISS
⏱ Dashboard view took: 0.0051 seconds
[31/May/2025 21:23:21] "GET / HTTP/1.1" 200 102078

✅ Cache HIT
⏱ Dashboard view took: 0.0012 seconds
[31/May/2025 21:23:23] "GET / HTTP/1.1" 200 102078

✅ Cache HIT
⏱ Dashboard view took: 0.0011 seconds
[31/May/2025 21:23:24] "GET / HTTP/1.1" 200 102078
```

The caching system is easy to configure and currently applies to the main dashboard view. It is especially useful when multiple users are posting or refreshing the timeline frequently.

## 🧰 Tech Stack

- 🐍 **Django** – Backend framework
- 🗄️ **SQLite** – Lightweight DB for local dev
- 🎨 **Bootstrap 5** – Responsive styling
- 🖱️ **Dropzone.js** – Drag & drop avatar upload
- 🖼️ **CSS Animations** – Twitter-like bird animation

## Why Django? 🎯

Dwitter was built using Django because it offers:

- Fast development with clean and pragmatic design
- Built-in security features (Authentication, CSRF protection)
- Excellent scalability for future enhancements

## Contributing 🤝

Feel free to submit issues or pull requests! Dwitter is open to community contributions.

## License 📜

MIT License - Feel free to use and modify as needed.

---

Happy coding with Dwitter! 🚀
