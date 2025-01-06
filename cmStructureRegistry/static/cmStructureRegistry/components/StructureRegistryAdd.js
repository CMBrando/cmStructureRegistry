export default {
    template: '#structure-add-bulk',
    data: function () {
        return {
            names: [],
            text: '',
            message: '',
            showMessage: false,
            showProcessing: false,
            messageType: 'success'
        };
    },
    mounted: function () {
    },
    methods: {
        onPaste: function(evt) {
            var raw = this.text;
            this.parseStructures(raw);
        },
        parseStructures: function(text) {
            this.names = text.split('  ');
            if (this.names.length == 1)
                this.names = text.split('\n');
        },
        addStructures: function () {

            var self = this;

            var token = this.$root.$data.token;
            var header = this.$root.$data.header;
            var ajaxHeaders = {};
            ajaxHeaders[header] = token;

            this.showProcessing = true;

            $.ajax({
                cache: false,
                type: 'POST',
                url: "AddStructures",
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify(this.names),
                dataType: "json",
                headers: ajaxHeaders
            }).done(function (data) {

                if (data.success) {
                    self.message = 'Structures added successfully';
                    self.messageType = 'success';
                    self.showMessage = true;
                    self.names = [];
                    self.text = '';
                }
                else {
                    self.message = data.message;
                    self.messageType = 'error';
                    self.showMessage = true;
                }

                self.showProcessing = false;

                setTimeout(function () {
                    self.showMessage = false;
                }, 5000);

            });

        }
    }
}

