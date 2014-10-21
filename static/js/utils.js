
/**
 * @param length: Length of random string
 * @return random string 
 */
function rand64(length) {
    var text = "";
    var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-";

    for (var i = length - 1; i >= 0; i--) {
    	text += alphabet.charAt(Math.floor(Math.random() * alphabet.length));
    }
    
    return text;
}
