document.addEventListener("DOMContentLoaded", () => {
  setupTweetShare();
  setupBirdAnimation();
  setupFollowButtons();
});

function setupTweetShare() {
  document.addEventListener("click", function (e) {
    if (e.target.matches("[data-share]")) {
      const tweetId = e.target.dataset.share;
      const url = `${window.location.origin}/tweet/${tweetId}/`;
      navigator.clipboard.writeText(url).then(() => {
        alert("Tweet link copied to clipboard!");
      });
    }
  });
}

function setupBirdAnimation() {
  const bird = document.querySelector(".logo-bird");
  if (bird) {
    bird.addEventListener("animationend", () => {
      bird.classList.remove("logo-bird");
      bird.classList.add("flap-finished");
    });
  }
}

function setupFollowButtons() {
  document.querySelectorAll("[data-follow]").forEach((btn) => {
    const endpointUrl = btn.dataset.url;
    const csrfToken = btn.dataset.csrf;
    const username = btn.dataset.username;

    btn.addEventListener("click", () => {
      const isFollowing = btn.dataset.following === "true";

      fetch(endpointUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `username=${encodeURIComponent(username)}`,
      })
        .then((res) => res.json())
        .then((data) => updateFollowButton(btn, data.status))
        .catch((err) => console.error("Follow error:", err));
    });
  });
}

function updateFollowButton(btn, status) {
  if (status === "followed") {
    btn.textContent = "Dejar de seguir";
    btn.classList.replace("btn-primary", "btn-danger");
    btn.dataset.following = "true";
  } else if (status === "unfollowed") {
    btn.textContent = "Seguir";
    btn.classList.replace("btn-danger", "btn-primary");
    btn.dataset.following = "false";
  }
}
