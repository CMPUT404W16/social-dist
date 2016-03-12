API
=============


.. http:get:: /users/(int:user_id)/posts/(tag)

   The posts tagged with `tag` that the user (`user_id`) wrote.

   **Example request**:

   .. sourcecode:: http

      GET /users/123/posts/web HTTP/1.1
      Host: example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: text/javascript

      [
        {
          "post_id": 12345,
          "author_id": 123,
          "tags": ["server", "web"],
          "subject": "I tried Nginx"
        },
        {
          "post_id": 12346,
          "author_id": 123,
          "tags": ["html5", "standards", "web"],
          "subject": "We go to HTML 5"
        }
      ]

   :query sort: one of ``hit``, ``created-at``
   :query offset: offset number. default is 0
   :query limit: limit number. default is 30
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: no error
   :statuscode 404: there's no user


Post API
----------

.. http:get:: /api/posts

    List all post which marked as public on the server.

.. http:get:: /api/posts/(int:post_id)

    Access a single post with `post_id`.

.. http:get:: /api/posts/(int:post_id)/comments

    Access the comments of the post with `post_id`.


Author API
----------

.. http:get:: /api/author/(str:author_id)

    Get the author's profiles.

  **Example response**:

  {
    "displayname": "cody", 
    "friends": [
        {
            "displayname": "friend1", 
            "host": "127.0.0.1:5000", 
            "id": "28e324124d144d41bebcdb9112efa104", 
            "url": "127.0.0.1:5000/author/853683c6120347aab99a37ccf5b1d3fa"
        }, 
        {
            "displayname": "friend2", 
            "host": "127.0.0.1:5000", 
            "id": "853683c6120347aab99a37ccf5b1d3fa", 
            "url": "127.0.0.1:5000/author/853683c6120347aab99a37ccf5b1d3fa"
        }
    ], 
    "host": "127.0.0.1:5000", 
    "id": "af6a29e580244bcaa31e4f7f078d3137", 
    "url": "127.0.0.1:5000/author/af6a29e580244bcaa31e4f7f078d3137"
  }    

.. http:get:: /api/author/posts

    Retrieval all visible posts to the currently authenticated user.

.. http:get:: /api/author/(str:author_id)/posts

    List all post which posted by `author_id`.


Friend API
-----------

.. http:get:: /api/friends/(str:author_id)/(str:author_id)

    Check whether two authors are friend or not.

    **Example response**:

    .. sourcecode:: http


    {
      "authors": [
        "28e324124d144d41bebcdb9112efa104", 
        "af6a29e580244bcaa31e4f7f078d3137"
      ], 
      "friends": true, 
      "query": "friends"
    }

.. http:get:: /api/friends/(str:author_id)

    Returns a list of author_id's friends.

    **Example response**:

    .. sourcecode:: http


    {
      "friends": [
        "b84b250afa7747f6a563b326ea161efb"
      ], 
      "query": "friends"
    }

.. http:post:: /api/friends/(str:author_id)

    Check whether an author is friends with other authors in a list of authors.

    **Example post**:

    .. sourcecode:: http

    {
      "query":"friends",
      "author":"<authorid>",
      "authors": [
        "de305d54-75b4-431b-adb2-eb6b9e546013",
        "ae345d54-75b4-431b-adb2-fb6b9e547891",
        "...",
        "...",
        "..."
      ]
    }   

    **Example response**:

    .. sourcecode:: http 

    {
      "query":"friends",
      "author":"9de17f29c12e8f97bcbbd34cc908f1baba40658e",
      "authors": [
        "de305d54-75b4-431b-adb2-eb6b9e546013",
        "ae345d54-75b4-431b-adb2-fb6b9e547891",
        "..."
      ]
    }

.. http:post:: /api/friendrequest

    Make a friend request.

    **Example post**:

    .. sourcecode:: http

    {
      "query":"friendrequest",
      "author": {
        "id":"de305d54-75b4-431b-adb2-eb6b9e546013",
        "host":"http://127.0.0.1:5454/",
        "displayName":"Greg Johnson"
      },
      "friend": {
        "id":"de305d54-75b4-431b-adb2-eb6b9e637281",
        "host":"http://127.0.0.1:5454/",
        "displayName":"Lara Croft",
        "url":"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e"
      }
    }   