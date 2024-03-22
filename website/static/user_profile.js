document.addEventListener('DOMContentLoaded', function () {
  const profileLinks = document.querySelectorAll('.user-name');

  profileLinks.forEach(link => {
    link.addEventListener('mouseover', function (event) {
      const firstName = this.innerText.trim();
      showUserProfile(firstName, event);
    });
  });

  // Dynamically create a style element and append it to the head
  const style = document.createElement('style');
  style.innerHTML = `
    .user-popup {
      position: fixed;
      z-index: 9999;
      background-color: #fff;
      border: 1px solid #ccc;
      padding: 10px;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
  `;
  document.head.appendChild(style);
});

function showUserProfile(firstName, event) {
  fetch("/get-user-profile/" + firstName)
      .then(response => response.json())
      .then(data => {
          const popup = document.createElement('div');
          popup.classList.add('user-popup');
          popup.innerHTML = `
              <img src="${data.avatar}" style="margin: 5px; float: left">
              <p><a href="/user/${data.name}">${data.name}</a></p>
              ${data.bio ? `<p>${data.bio}</p>` : ''}
              ${data.last_seen ? `<p>Last seen on: ${moment(data.last_seen).format('lll')}</p>` : ''}
              <p>${data.followers} followers</p>
              <form action="/follow/${data.name}" method="post">
                  <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">
                  <button type="submit" class="btn btn-outline-primary btn-sm">${data.is_following ? 'Unfollow' : 'Follow'}</button>
              </form>
          `;

          // Append the popup to the body
          document.body.appendChild(popup);

          // Get mouse coordinates from the event object
          const mouseX = event.clientX;
          const mouseY = event.clientY;

          // Position the popup near the mouse cursor, considering viewport boundaries
          popup.style.display = 'block'; // Show the popup
          popup.style.top = `${Math.min(mouseY + 10, window.innerHeight - popup.offsetHeight - 10)}px`; // Adjust for viewport boundaries
          popup.style.left = `${Math.min(mouseX + 10, window.innerWidth - popup.offsetWidth - 10)}px`; // Adjust for viewport boundaries

          // Remove the popup after 2 seconds
          setTimeout(() => {
            popup.remove();
          }, 2000);
      })
      .catch(error => console.error('Error:', error));
}
