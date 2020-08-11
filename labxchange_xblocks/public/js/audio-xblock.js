function LXAudioXBlock(runtime, element, init_args) {
    'use strict';

    var LanguageSelector = function(element_id, user_state) {
        this.user_state = user_state;
        this.element = $('.' + element_id, element);
        this.currentLang = user_state.current_lang || '';
        this.getSequencesUrl = runtime.handlerUrl(element, 'sequences');

        this.init();
    }

    LanguageSelector.prototype.init = function() {
        var that = this;
        this.element.on('change', function() {
            console.log(this.value)
            that.getSequences(this.value)
        })
        this.getSequences(this.currentLang);
    }

    LanguageSelector.prototype.getSequences = function(lang) {
        $.ajax({
            url: this.getSequencesUrl,
            data: JSON.stringify({'lang': lang}),
            contentType: 'application/json',
            method: 'POST',
        }).done(function(data) {
            var element = $('.audio-block-sequences-student-view');
            element.html('');
            data.map(function(sequence, index) {
                console.log(sequence)
                element.append(
                    '<div class="audio-block-sequences-line-student-view">' +
                        '<div class="audio-block-sequences-start-student-view">' +
                            `${sequence.start.hours}:${sequence.start.minutes}:${sequence.start.seconds}` +
                        '</div>' +
                        '<div class="audio-block-sequences-text-student-view">' +
                            `${sequence.text}` +
                        '</div>' +
                    '</div>'
                );
            })
        });
    }

    var languageSelector = new LanguageSelector(
        'audio-block-transcript-select',
        init_args.user_state,
    );
}
