#Model Design

1. User
	- ID *
	- UUID

		A. Local
		
				- Username
				- Password
				- Email
				- Role (could be Admin, User...) ~
				- Posts ~
				
		B. Remote
		
				- Node ID
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
	- UID 

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


