function addSong() {
    // Clone the last song container
    var lastSongContainer = document.querySelector('.song-container:last-child');
    var newSongContainer = lastSongContainer.cloneNode(true);

    // Clear input values in the cloned container
    var inputs = newSongContainer.querySelectorAll('input');
    inputs.forEach(function (input) {
        input.value = '';
    });

    // Append the cloned container to the songs-container
    document.getElementById('songs-container').appendChild(newSongContainer);
}