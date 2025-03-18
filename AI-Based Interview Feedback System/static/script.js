let recognition;
if ("webkitSpeechRecognition" in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";
} else {
    alert("Your browser does not support speech recognition.");
}

let fullTranscript = "";
let liveTextDisplay = document.getElementById("liveText");

// Start Recording
function startRecording() {
    document.getElementById("status").innerText = "Recording...";
    document.getElementById("stopBtn").disabled = false;
    fullTranscript = "";
    liveTextDisplay.innerHTML = "";
    recognition.start();
}

document.getElementById("recordBtn").addEventListener("click", startRecording);

document.getElementById("stopBtn").addEventListener("click", function() {
    document.getElementById("status").innerText = "Processing speech...";
    recognition.stop();
});

// Process Speech Recognition in Real-Time
recognition.onresult = function(event) {
    fullTranscript = "";
    let displayedText = "";
    
    for (let i = 0; i < event.results.length; i++) {
        let transcript = event.results[i][0].transcript;
        fullTranscript += transcript + " ";
        displayedText += `<p>${transcript}</p>`;
    }
    
    liveTextDisplay.innerHTML = displayedText; // Display all live speech continuously
};

// Send Final Speech to Backend for Analysis
recognition.onend = function() {
    document.getElementById("status").innerText = "Analyzing speech...";
    fetch("/process_speech", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: fullTranscript })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("transcribedText").innerText = data.transcribed_text;
        document.getElementById("sentiment").innerText = data.evaluation.sentiment;
        document.getElementById("fluency").innerText = data.evaluation.fluency;
        document.getElementById("vocabulary").innerText = data.evaluation.vocabulary;
        document.getElementById("confidence").innerText = data.evaluation.confidence;
        document.getElementById("repeatedWords").innerText = data.evaluation.repeated_words.join(", ");
        document.getElementById("hesitations").innerText = data.evaluation.hesitations;
        document.getElementById("grammarIssues").innerText = data.evaluation.grammar_issues.join(", ");
        document.getElementById("suggestions").innerText = data.evaluation.suggestions.join("\n");
    });
};