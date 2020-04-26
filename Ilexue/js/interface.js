function getraw(username,plainPassword){
    let raw = 'tenantCode=default&username='+username+'&tenantid=-1&warn=true&lt=&execution=&_eventId=submit';
    let exponent = '10001'
    let modulus = 'b4c04a1197e743368183f83b46b6f194fbb5aed66f9868f1f8ad1c046c677d3493e550440bae5bf17631bcb945b6b5066232515c81016fa943e3526146ec5e624ee39edec364c142d873b328a2323a4f0edaf3c0d91bfcf765313503c112960b20af75faf1bb370f5392183f45ff3171904fa6017decb0f45c8fe6c306c204ef';
    let key = RSAUtils.getKeyPair(exponent, '', modulus);
    let tokeninfo = RSAUtils.encryptedString(key, plainPassword) + '_encrypted';
    raw = raw+'&tokeninfo='+tokeninfo;
    raw = raw+'&isAutoLogin=0&randomvalue=1582782438032';
    let shaPassword = rsa1value(plainPassword);
    raw = raw+'&shaPassword='+shaPassword;
    let md5Password = hex_md5(plainPassword);
    raw = raw+'&md5Password='+md5Password;
    let validateCode = '';
    // let validateKey = 1582782453000;
    let validateKey = Date.parse(new Date());
    raw = raw+'&validateCode='+validateCode;
    raw = raw+'&validateKey='+validateKey;
    return raw;
}

function rsa1value(val) {
    var shaObj = new jsSHA("SHA-1", "TEXT");
    shaObj.update(val);
    var hash = shaObj.getHash("HEX");
    return hash
}