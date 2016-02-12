1. User

		- UID *
		- UUID(Universal)

		A. Local
		
				- Username
				- Password
				- Email
				- Role (could be aAdmin, User...) ~
				- Posts ~
				
		B. Remote
		
				- Node ID ~
				- UID
	
2. Post

		- Post ID *
		- User ID ~
		- Title
		- Text
		- Images ~
		- Markup
		- Privacy ID ~

3. Comment

		- Post ID ~
		- Comment ID *		
		- Content
		- UID ~

4. Images

		- Image ID * 		
		- Post ID ~
		- Image file
		
5. Role

		- Role ID *
		- Role name
		- Permissions

6. Permission

		- Permission ID *
		- Permission name

7. Privacy

		- Privacy name
		- Privacy ID *

8. Friend

		- FriendA ID *
		- FriendB ID *

9. Follow 
 
		- Requester ID *
		- Requestee ID *
		- isRejected

10. Node
 
		- Node ID *
		- IP Address
		- Auth code
	
11. API Request
 
		- Request ID *
		- HTTP Request Type
		- Request Type(Add friends, delete friends...)

12. Node API
 
		- Node ID *
		- Request ID *
		- URI

