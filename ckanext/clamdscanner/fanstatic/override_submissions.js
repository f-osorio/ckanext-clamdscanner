// Get the uploaded file and
// pass it to the clamdscanner.
// If it's OK, then continue the
// upload. Otherwise, display a
// message to the user.

// add "n" to _submissio
ckan.module('override_submissio', function(jQuery, _){
    return {
        options: {
            i18n: {
                heading: _('Scanning File'),
                content: _('Please wait while your file is scanned.'),
              },
            template: [
        '<div class="modal">',
        '<div class="modal-header">',
        '<button type="button" class="close" data-dismiss="modal">×</button>',
        '<h2></h2>',
        '</div>',
        '<div class="modal-body"></div>',
        '<div class="modal-footer">',
        '</div>',
        '</div>'
            ].join('\n')
        },
        initialize: function(){
            jQuery.proxyAll(this, /_on/);
            console.log('Working?', this.el);
            this.el.on('click', this._onClick);
        },

        _onClick: function(event){
            event.preventDefault();
            this.scan(event);
        },

        createModal: function () {
          if (!this.modal) {
            var element = this.modal = jQuery(this.options.template);
            element.modal({show: false});

            element.find('h2').text(this.i18n('heading'));
            element.find('.modal-body').html(this.i18n('content'));
          }
          return this.modal;
        },

        _updateModal: function(modal, data){
            if (data[0]){
                var content = "Success! File was scanned with no issues.";
            } else {
                var content = "Scan Failed. Found \"" +data[1]+ "\" in file.";
            }

            modal.find('.modal-body').html(content);

            modal.find('h2').text("Scan Complete");

        },

        scan: function(event){
            // launch modal
            this.sandbox.body.append(this.createModal());
            this.modal.modal('show');
            this.modal.css({
                'margin-top': this.modal.height() * -0.5,
                'top': '50%'
            });

            var file_field = document.getElementById('field-image-upload');
            var file = file_field.files[0];
            var reader = new FileReader();
            //reader.readAsBinaryString(file);
            reader.readAsArrayBuffer(file);
            var sandbox = this.sandbox;
            var updateModal = this._updateModal;
            var modal = this.modal;
            reader.onload = function(e){
                var result = reader.result;
                console.log(file);
                console.log('R:', result);
                sandbox.client.call('POST',
                                    'scan',
                                    {data: result},
                                    function(json){
                                        var result = json.result;
                                        console.log(json);
                                        if (! result[0]){
                                            //Failed
                                            updateModal(modal, result);
                                        } else {
                                            // passed
                                            updateModal(modal, result);
                                        }
                                    },
                                    function(e){
                                        console.log('Error', e);
                                    });
            }
        }
    }
});
