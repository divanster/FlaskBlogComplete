document.addEventListener('DOMContentLoaded', function() {
    fetch('/get_followers/{{ username }}')
        .then(response => response.json())
        .then(data => {
            const followersList = document.getElementById('followers-list');
            data.forEach(follower => {
                const followerDiv = document.createElement('div');
                followerDiv.innerHTML = `Username: ${follower.username}, Email: ${follower.email}`;
                followersList.appendChild(followerDiv);
            });
        });
});