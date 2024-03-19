from flask import Flask,render_template,redirect,request,session,send_from_directory
from web3 import Web3,HTTPProvider
import json
from werkzeug.utils import secure_filename
import qrcode
from io import BytesIO

def connectWithBlockchain():
    web3=Web3(HTTPProvider('http://127.0.0.1:7545'))
    web3.eth.defaultAccount=web3.eth.accounts[0]

    artifactPath='../build/contracts/QRGuide.json'
    with open(artifactPath) as f:
        artficat_json=json.load(f)
        contract_abi=artficat_json['abi']
        contract_address=artficat_json['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=contract_abi,address=contract_address)

    return contract,web3

app=Flask(__name__)
app.secret_key='1234'
app.config["UPLOAD_FOLDER"] = "uploads/"

@app.route('/')
def homePage():
    contract,web3=connectWithBlockchain()
    _filepaths,_productcosts,_productlocations,_productnames,_productids=contract.functions.viewProducts().call()
    data=[]
    for i in range(len(_filepaths)):
        dummy=[]
        dummy.append(_productids[i])
        dummy.append(_productnames[i])
        data.append(dummy)
    return render_template('index.html',data=data)

@app.route('/queryproduct',methods=['POST','GET'])
def queryproduct():
    if request.method=='POST':
        prodid=request.form['prodid']
    else:
        prodid=request.args.get('prodid')
    
    contract,web3=connectWithBlockchain()
    _filepaths,_productcosts,_productlocations,_productnames,_productids=contract.functions.viewProducts().call()
    data1=[]
    data=[]

    for i in range(len(_filepaths)):
        dummy=[]
        dummy.append(_productids[i])
        dummy.append(_productnames[i])
        data.append(dummy)

    for i in range(len(_filepaths)):
        if _productids[i]==int(prodid):
            dummy=[]
            dummy.append(_filepaths[i])
            dummy.append(_productcosts[i])
            dummy.append(_productlocations[i])
            dummy.append(_productnames[i])
            dummy.append(_productids[i])
            data1.append(dummy)
    
    return render_template('index.html',data=data,data1=data1)


@app.route('/contactUs',methods=['POST'])
def contactUs():
    firstname=request.form['firstname']
    lastname=request.form['lastname']
    Area=request.form['Area']
    subject=request.form['subject']
    print(firstname,lastname,Area,subject)
    return render_template('index.html',res='Message Updated')

@app.route('/location')
def location():
    return render_template('Location.html')

@app.route('/login')
def login():
    return render_template('userlogin.html')

@app.route('/admin')
def admin():
    return render_template('Login.html')

@app.route('/adminloginform',methods=['POST'])
def adminloginform():
    username=request.form['username']
    password=request.form['password']
    if username=='admin' and password=='admin123':
        session['username']='admin'
        return redirect('/admindashboard')
    else:
        return render_template('Login.html',err='invalid login')

@app.route('/dashboard')
def dashboard():
    contract,web3=connectWithBlockchain()
    _filepaths,_productcosts,_productlocations,_productnames,_productids=contract.functions.viewProducts().call()
    data=[]
    for i in range(len(_filepaths)):
        dummy=[]
        dummy.append(_filepaths[i])
        dummy.append(_productcosts[i])
        dummy.append(_productlocations[i])
        dummy.append(_productnames[i])
        data.append(dummy)
    return render_template('Products.html',data=data)

@app.route('/admindashboard')
def admindashboard():
    return render_template('admindashboard.html')

@app.route('/products')
def products():
    return render_template('Products.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signupform',methods=['POST'])
def signupform():
    email=request.form['email']
    psw=request.form['psw']
    pswrepeat=request.form['pswrepeat']
    
    if(psw!=pswrepeat):
        return render_template('signup.html',err='Passwords didnt matched')
    
    contract,web3=connectWithBlockchain()
    
    try:
        tx_hash=contract.functions.signup(email,psw).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return render_template('signup.html',res='account created')
    except:
        return render_template('signup.html',err='Account Exist')

@app.route('/loginform',methods=['POST'])
def loginform():
    username=request.form['username']
    password=request.form['password']

    contract,web3=connectWithBlockchain()
    _emails,_passwords=contract.functions.viewUsers().call()

    for i in range(len(_emails)):
        if _emails[i]==username and _passwords[i]==password:
            session['username']=username
            return redirect('/dashboard')
    
    if username in _emails:
        return render_template('login.html',err='login invalid')
    else:
        return render_template('login.html',err='signup first')

@app.route('/logout')
def logout():
    session['username']=None
    return redirect('/')

@app.route('/addproductform',methods=['post'])
def addproductform():
    chooseFile=request.files['chooseFile']
    productcost=request.form['productcost']
    productname=request.form['productname']
    productlocation=request.form['productlocation']
    doc1=secure_filename(chooseFile.filename)
    chooseFile.save('uploads'+'/'+doc1)
    print(chooseFile,productcost,productname,productlocation)
    contract,web3=connectWithBlockchain()
    tx_hash=contract.functions.addProduct('uploads'+'/'+doc1,productcost,productname,productlocation).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)

    contract,web3=connectWithBlockchain()
    _filepaths,_productcosts,_productlocations,_productnames,_productids=contract.functions.viewProducts().call()
    for i in range(len(_filepaths)):
        if _filepaths[i]=='uploads'+'/'+doc1:
            productId=_productids[i]
            qr = qrcode.make(productId)
            img = BytesIO()
            qr.save(img, 'PNG')
            img.seek(0)
    
            # Save QR code as a file
            filename = 'uploads/'+ str(productId)+'.png'
            qr.save(filename)
            return render_template('admindashboard.html',res='Product Added')
    return render_template('admindashboard.html',err='Product Added Error')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/myproducts')
def myproducts():
    contract,web3=connectWithBlockchain()
    _filepaths,_productcosts,_productlocations,_productnames,_productids=contract.functions.viewProducts().call()
    data=[]
    for i in range(len(_filepaths)):
        dummy=[]
        dummy.append(_filepaths[i])
        dummy.append(_productcosts[i])
        dummy.append(_productlocations[i])
        dummy.append(_productnames[i])
        data.append(dummy)
    return render_template('myproducts.html',data=data)

if __name__=="__main__":
    app.run(host='0.0.0.0',port=9001,debug=True)