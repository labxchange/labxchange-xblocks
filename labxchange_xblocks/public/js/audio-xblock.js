function LXAudioXBlock(runtime, element, init_args) {
    'use strict';

    var LanguageSelector = function(element_selector, user_state) {
        this.user_state = user_state;
        this.element = $('.' + element_selector, element);
        this.sequencesElement = this.element.find('.audio-block-sequences-student-view');
        this.currentLang = user_state.current_lang || '';
        this.getSequencesUrl = runtime.handlerUrl(element, 'sequences');
        this.init();
    }

    LanguageSelector.prototype.init = function() {
        var self = this;
        this.element.find('.audio-block-transcript-select')
                    .on('change', function() {
            self.getSequences(this.value)
        })
        this.getSequences(this.currentLang);
        this.element.find()
    }

    LanguageSelector.prototype.getSequences = function(lang) {
        var sequencesElement = this.sequencesElement;
        $.ajax({
            url: this.getSequencesUrl,
            data: JSON.stringify({'lang': lang}),
            contentType: 'application/json',
            method: 'POST',
        }).done(function(data) {
            sequencesElement.html('');
            data.map(function(sequence, index) {
                sequencesElement.append(
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
        'audio-block-student-view',
        init_args.user_state,
    );
}
