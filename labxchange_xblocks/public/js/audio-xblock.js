// TODO: delete this once https://tasks.opencraft.com/browse/LX-2243 is complete
function LXAudioXBlock(runtime, element, init_args) {
    'use strict';

    var LanguageSelector = function(element_selector, user_state) {
        this.user_state = user_state;
        this.element = $('.' + element_selector, element);
        this.sequencesElement = this.element.find('.audio-block-sequences-student-view');
        this.toggleElement = this.element.find('.audio-block-transcript-toggle');
        this.currentLang = user_state.current_lang || '';
        this.folded = false;
        this.getSequencesUrl = runtime.handlerUrl(element, 'sequences');
        this.init();
    }

    LanguageSelector.prototype.init = function() {
        var self = this;
        this.element.find('.audio-block-transcript-select')
                    .on('change', function() {
            self.getSequences(this.value);
        });
        this.getSequences(this.currentLang);
        this.element.find('.audio-block-transcript-toggle')
            .on('click', function() { self.toggleBlock(); });
    }

    LanguageSelector.prototype.getSequences = function(lang) {
        var sequencesElement = this.sequencesElement;
        $.ajax({
            url: this.getSequencesUrl + '?lang=' + lang,
            method: 'GET',
        }).done(function(data) {
            sequencesElement.html(data.content);
        });
    }

    LanguageSelector.prototype.toggleBlock = function() {
        this.folded = !this.folded;
        this.sequencesElement.toggle();
        if (this.folded) {
            this.element.removeClass('unfolded');
            this.element.addClass('folded');
        } else {
            this.element.addClass('unfolded');
            this.element.removeClass('folded');
        }
    }

    var languageSelector = new LanguageSelector(
        'audio-block-student-view',
        init_args.user_state,
    );
}
