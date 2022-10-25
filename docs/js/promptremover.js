document.addEventListener("DOMContentLoaded", function(){
    //....
    const collection = document.getElementsByClassName("highlight");
    for (let i = 0; i < collection.length; i++) {
        //const commandTextElement = collection[i].getElementsByTagName("code");
        const commandElement=collection.item(i);
        //const commandText=commandTextElement.innerHTML;
        console.log(commandElement);
        let commandCodeElement = commandElement.getElementsByTagName("code");
        //console.log(commandCodeElement);
        let commandCodeElementString = commandCodeElement.item(0).textContent;
        //console.log(commandCodeElementString);
        let trueCommand = commandCodeElementString;
        if (commandCodeElementString.startsWith("$")) {
            trueCommand = commandCodeElementString.substring(2, commandCodeElementString.length).trim();
        }
        console.log(trueCommand);
        let commandButtonElement = commandElement.getElementsByTagName("button");
        console.log(commandButtonElement);
        commandButtonElement.item(0).setAttribute("data-clipboard-text", trueCommand);
    }
});





