$(document).ready(function() {
    // Add click event listener to the "like" button
    $('.like-btn').on('click', function(event) {
        // Prevent the default form submission behavior
        event.preventDefault();

        // Get the ID of the user, blog_post, and comment from the data attributes of the "like" button
        var userId = $(this).data('user-id');
        var blogPostId = $(this).data('blog-post-id');
        var commentId = $(this).data('comment-id');

        // Send an AJAX request to the server to create the like
        $.ajax({
            type: 'POST',
            url: '/like',
            contentType: 'application/json',
            data: JSON.stringify({
                user_id: userId,
                blog_post_id: blogPostId,
                comment_id: commentId
            }),
            success: function(response) {
                // Update the like count on the client side
                var likeCount = $('#like-count-' + blogPostId).text();
                $('#like-count-' + blogPostId).text(parseInt(likeCount) + 1);

                // Disable the "like" button after the user has liked the post
                $('.like-btn').prop('disabled', true);
            },
            error: function(xhr, status, error) {
                console.error('Error creating like:', error);
            }
        });
    });
});
