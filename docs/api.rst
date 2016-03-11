Api Endpoints
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

.. http:get:: /api/author/posts

    Retrieval all visible posts to the currently authenticated user.

.. http:get:: /api/author/(str:author_id)/posts

    List all post which posted by `author_id`.


Friend API
-----------

.. http:get:: /api/friends/(str:author_id)/(str:author_id)

    Check whether two authors are friend or not.

.. http:post:: /api/friends/(str:author_id)

    Check whether an author is friends with other authors in a list of authors.

.. http:post:: /api/friendrequest

    Make a friend request.


