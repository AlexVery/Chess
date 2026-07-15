<div align="center">

# Chess Game

</div>

  The goal of this project was to create the chess game from scratch. 
  The game consists of 7 files:
  - **bapp_state.py**: contains the AppState object resposible for executing the app (running the game and handling the user log in/ sign up).
  - **button.py**: object to implement a button, that changes color upon hovering over it and call a function when clicked on.
  - **game_state.py**: GameState object handles the game mechanics, from handling moves (and checking whether special moves like en pasant or
    castling are available) to rendering the game board.
  - **helper_functions.py**: general functions that help build the game, that includes draw functions, functions to get username inputs etc.
  - **load_game_save_data.py**: an example representation of the game data saved is present there. Functions that register or log in the user
    are implemented there.
  - **main.py**: includes the main function of the app, includes the rest 6 files and calls the main execution method of the AppState object.
  - **pieces.py**: the logic behind each piece type is implemented: pawn, knight, bishop, rook, queen and king. Some pieces require extra methods,
    for example the king can perform an extra move 'castling' and the pawns one called 'en passant'.

<div align="center">


  In the beginning there is a welcome screen, where players must register or log in into their accounts, as seen in *Figure 1*:
  
  <p align="center">
    <img width="627" height="516" alt="Image" src="https://github.com/user-attachments/assets/dd16fe9b-41d2-4448-90d6-2e3a66f732d0" />
  </p>
  
  
  **Figure 1**: Log in/ sign up screen

</div>

  The log in screen can be seen in *Figure 2*. It also includes a hide/ show password feature, triggering it by just clicking 
  on the icon to the right of the password box. The hide/show password feature is presented in *Figure 3* and *Figure 4* respectively.

<div align="center">
  
  <p align="center">
    <img width="626" height="511" alt="Image" src="https://github.com/user-attachments/assets/7a6896c7-d2da-4562-b12a-6f70ab8d85f3" />
  </p>

  **Figure 2**: Log in screen

  <p align="center">
    <img width="625" height="518" alt="Image" src="https://github.com/user-attachments/assets/c2fee608-1ba8-4d06-9d87-f20a42be43f4" />
  </p>

  **Figure 3**: Log in screen - Hide password

  <p align="center">
    <img width="623" height="503" alt="Image" src="https://github.com/user-attachments/assets/8ef62d46-af77-42c6-96e3-e1601c760884" />
  </p>

  **Figure 4**: Log in screen - Show password

</div>
  
  There is a typical password check,
  with ui elements helping the players understand the requirements to create a new password (length, minimum of 1 character or number, etc.).
  The 'Log in', 'Sign up' buttons change dynamically. The system checks whether the provided username exists in the game data file,
  in which case creates a 'Log in' button, else a registration is needed and a 'Sign up' button replaces it (*Figure 5*). The red circles on 
  the left of each rect represents the log in state of each player, it only becomes green if the respective user is logged in or a new user is
  correctly registered.

<div align="center">

  <p align="center">
    <img width="622" height="511" alt="Image" src="https://github.com/user-attachments/assets/d4c048e6-de82-4005-aaa8-f5b0ab38c12b" />
  </p>

  **Figure 5**: Log in/ sign up screen (Sign up present)

</div>

  The registration screen can be seen in *Figure 6* and the hide/show password feature in *Figures 7, 8*. The requirements fulfilled are marked
  with a green circle to the left of the text, while the unfulfilled with a red one.

<div align="center">

  <p align="center">
    <img width="626" height="518" alt="Image" src="https://github.com/user-attachments/assets/5c5067b0-6926-4282-a75e-91b80179f28d" />
  </p>

  **Figure 6**: Sign up screen

  <p align="center">
    <img width="625" height="513" alt="Image" src="https://github.com/user-attachments/assets/af3a1e23-c96a-4979-98f2-16fe61f284cf" />
  </p>

  **Figure 7**: Sign up screen - Hide password

  <p align="center">
    <img width="624" height="516" alt="Image" src="https://github.com/user-attachments/assets/f0561d24-face-45c3-a4bb-c383cacbe28d" />
  </p>

  **Figure 8**: Sign up screen - Show password

</div>

  After logging in the game begins. On the right of the screen there are ui elements to help players keep track of important stats, for example
  each player's turn is written with the same color as the pieces they're playing with, that means that if PlayerA plays as white and PlayerB as
  black, then 'PlayerA' turn' is going to be written in white and the same message for PlayerB in black. It also features a 'Main Menu' button
  in case players want to switch colors or even players (logging off). The game also provides a half-move counter (one move consists of two half-
  moves, with each player making one half-move each turn), to inform them of the 50 and 75-move rule (no pawns moved and no pieces captured), 
  which results in a draw. It also includes a message for the number of occurrences for each move, to keep track of the threefold and fivefold
  rule (which also results in a draw). This means that after each move the board is in a specific state and we can actually create a hash key to
  help us keep track of the number of times each state has occurred. If a state has occured 3 or 4 times the player to play can request a draw,
  a fifth time means an automatic draw. All these features can be seen in *Figure 9*.

<div align="center">

  <p align="center">
    <img width="628" height="516" alt="Image" src="https://github.com/user-attachments/assets/41ed89c3-6c75-4ab3-aaf0-d825a7e5083c" />
  </p>

  **Figure 9**: Main game screen

</div>
  
  To move a piece player must click on the desired piece and all the available moves are going to be displayed
  either with a green or red circle in the middle of each available square. Red means the piece captures an enemy piece, green simply moves the 
  piece to the desired square. It is also possible that the selected piece doesn't have any moves available, resulting in no circles present 
  on the board. The number of captured pieces are displayed along an image for each piece type (*Figures 10, 11*).

<div align="center">

  <p align="center">
    <img width="623" height="513" alt="Image" src="https://github.com/user-attachments/assets/29305fc4-0108-484d-9ae5-fff724000130" />
  </p>

  **Figure 10**: Piece selection

</div>

<div align="center">

  <p align="center">
    <img width="620" height="515" alt="Image" src="https://github.com/user-attachments/assets/f52a7d63-24f4-4006-a235-13a01f210230" />
  </p>

  **Figure 11**: Available moves (marked with green and red) for selected piece

</div>

If the player decides to capture a pawn, then the captured pawn is removed from the board and the counter for the captured pieces of same
color and type is increased by one, as seen in *Figure 12*.

<div align="center">

  <p align="center">
    <img width="621" height="513" alt="Image" src="https://github.com/user-attachments/assets/7c8781ea-25ef-41b1-940a-72d53d24b14e" />
  </p>

  **Figure 12**: Captured pieces change

</div>

When the king is checked the king's square is marked with red (*Figure 13*) and player is forced to make a move that unchecks his king, if no such
move exists then it is a checkmate and the opponent wins (*Figure 14*).

<div align="center">

  <p align="center">
    <img width="621" height="513" alt="Image" src="https://github.com/user-attachments/assets/385611b4-9fe3-41d1-9c84-4a1412de2118" />
  </p>

  **Figure 13**: Check

  <p align="center">
    <img width="623" height="513" alt="Image" src="https://github.com/user-attachments/assets/3260329d-6eff-4eeb-bcae-7f165c3689cc" />
  </p>

  **Figure 14**: Checkmate

</div>

  If a pawn reaches the end of the board it must be promoted (*Figure 15*). The available pieces are seen in *Figure 16* (queen, rook, bishop, 
  knight) and the promotion in *Figure 17*.

  <div align="center">

  <p align="center">
    <img width="619" height="513" alt="Image" src="https://github.com/user-attachments/assets/172d5ca7-104d-40e6-9ab4-3c82262626fe" />
  </p>

  **Figure 15**: Pawn to reach promotion

  <p align="center">
    <img width="622" height="514" alt="Image" src="https://github.com/user-attachments/assets/5efa6e46-6196-4602-aa82-212500dd4ebb" />
  </p>

  **Figure 16**: Promotion screen

  <p align="center">
    <img width="621" height="516" alt="Image" src="https://github.com/user-attachments/assets/e2be57f3-e8fd-4fa5-baca-019f125868aa" />
  </p>

  **Figure 17**: Promoted to Queen

</div>
