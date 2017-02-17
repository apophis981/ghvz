'use strict';

class ServerBridge {
  sendLogInLink(email) { console.error('called base login', this, arguments); }
  logIn(email, code) { console.error('called base login', this, arguments); }
  addUser(email) { console.error('called base addUser', this, arguments); }
}
