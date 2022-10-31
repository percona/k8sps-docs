document.addEventListener("DOMContentLoaded", function(){
    //....
    const collection = document.getElementsByClassName("highlight");
    for (let i = 0; i < collection.length; i++) {
        //const commandTextElement = collection[i].getElementsByTagName("code");
        const commandElement=collection.item(i);
        //const commandText=commandTextElement.innerHTML;
        //console.log(commandElement);

        let commandButtonElement = commandElement.getElementsByTagName("button");
        let promptString = commandButtonElement.item(0).getAttribute("data-prompt");
        //console.log(commandCodeElement);
        if (!promptString) return;
        let commandCodeElement = commandElement.getElementsByTagName("code");
        let commandCodeElementString = commandCodeElement.item(0).textContent;
        //console.log(commandCodeElementString);
        let trueCommand = commandCodeElementString;
        if (commandCodeElementString.startsWith(promptString)) {
            trueCommand = commandCodeElementString.substring(promptString.length, commandCodeElementString.length).trim();
        }
        //console.log(trueCommand);
        
        //console.log(commandButtonElement);
        commandButtonElement.item(0).setAttribute("data-clipboard-text", trueCommand);
    }
});





