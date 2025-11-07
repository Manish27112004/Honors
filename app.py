from flask import Flask, request, jsonify, make_response
import secrets, time

app = Flask(__name__)

# Store sessions in memory (temporary)
sessions = {}
SESSION_TIMEOUT = 60  # 1 minute

@app.route('/')
def home():
    return """
    <h3>Simple Session Demo</h3>
    <input id='user' placeholder='Username'>
    <input id='pass' placeholder='Password' type='password'>
    <button onclick='login()'>Login</button>
    <button onclick='check()'>Check Session</button>
    <button onclick='logout()'>Logout</button>
    <p id='out'></p>
    <script>
      async function login() {
        let u=document.getElementById('user').value;
        let p=document.getElementById('pass').value;
        let res=await fetch('/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({u,p})});
        document.getElementById('out').innerText=(await res.json()).msg;
      }
      async function check(){
        let res=await fetch('/check');
        document.getElementById('out').innerText=(await res.json()).msg;
      }
      async function logout(){
        let res=await fetch('/logout');
        document.getElementById('out').innerText=(await res.json()).msg;
      }
    </script>
    """

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    u, p = data['u'], data['p']
    if u == "user" and p == "pass":  # simple check
        token = secrets.token_hex(8)
        sessions[token] = time.time() + SESSION_TIMEOUT
        resp = make_response(jsonify({'msg': 'Login successful'}))
        resp.set_cookie('token', token, httponly=True, samesite='Strict')
        return resp
    return jsonify({'msg': 'Invalid credentials'})

@app.route('/check')
def check():
    token = request.cookies.get('token')
    if not token or token not in sessions:
        return jsonify({'msg': 'No session / Not logged in'})
    if time.time() > sessions[token]:
        del sessions[token]
        return jsonify({'msg': 'Session expired'})
    return jsonify({'msg': 'Session active!'})

@app.route('/logout')
def logout():
    token = request.cookies.get('token')
    sessions.pop(token, None)
    resp = make_response(jsonify({'msg': 'Logged out'}))
    resp.delete_cookie('token')
    return resp

if __name__ == '__main__':
    app.run(debug=True)
