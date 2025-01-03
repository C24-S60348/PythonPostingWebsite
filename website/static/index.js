function deletePosting(postingId) {
    fetch('/delete_posting',
        {
            method: 'POST',
            body: JSON.stringify({postingId : postingId})
        }
    ).then((_res) => {
        window.location.href = '/';
    })
}
function deleteComment(commentId) {
    fetch('/delete_comment',
        {
            method: 'POST',
            body: JSON.stringify({commentId : commentId})
        }
    ).then((_res) => {
        window.location.href = '/';
    })
}

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});