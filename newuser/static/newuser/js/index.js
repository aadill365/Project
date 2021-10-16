function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
      function like(postId) {
        const likeCount = document.getElementById(`likes-count-${postId}`);
        const likeButton = document.getElementById(`like-button-${postId}`);

        // var csrftoken = Cookies.get('csrftoken');
        fetch(`/post/like/${postId}`,{method:'POST',credentials: "same-origin",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Accept": "application/json",
          'Content-Type': 'application/json'
        },
            
        }).then((res) => res.json())
        .then((data)=>{
            likeCount.innerHTML = data["count"];
            if(data["liked"] == true){
            likeButton.className = "fas fa-thumbs-up";

            }
            else{
            likeButton.className = "far fa-thumbs-up";


            }
        });
    }

    function follow(userId){
        const followButton = document.getElementById(`follow-${userId}`);
        const followerCount = document.getElementById(`follower-count-${userId}`);
        fetch(`/follow/${userId}/`,{method:'POST',credentials: "same-origin",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Accept": "application/json",
          'Content-Type': 'application/json'
        },
    }).then((result) => result.json())
        .then((data) =>{
            followerCount.innerHTML = data["count"];
            if(data["follow"] == true){
            followButton.className = "btn btn-outline-dark btn-sm px-5 py-0";
            followButton.innerHTML = "Unfollow";

            }
            else{
            followButton.className = "btn btn-primary btn-sm px-5 py-0";
            followButton.innerHTML = "Follow";


            }
        });


    }

    function save(postId){

        var saveButton = document.getElementById(`save-${postId}`);

        fetch(`/save/${postId}/`,{method:'POST',credentials: "same-origin",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Accept": "application/json",
          'Content-Type': 'application/json'
        },
    }).then((result) => result.json())
        .then((data) =>{
            if(data.save == true){
            saveButton.className = "fas fa-bookmark";
            }
            else{
            saveButton.className = "far fa-bookmark";
            }
        });
    }