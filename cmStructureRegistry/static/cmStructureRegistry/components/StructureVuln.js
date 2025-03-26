export default {
    template: '#structure-vulnerability',
    props: ['structure_id'],
    data: function () {
        return {
            vuln: '',
            vuln_list: [],
            structure_name: '',
            struct_vuln_text: '',
            next_vuln: null,
            next_vuln_date: null
        };
    },
    mounted: function () {

        var arr = _.range(24);
        this.vuln_list = _.map(arr, function (a) { return ('' + a).padStart(2, '0') + '00'; });
        this.vuln_list.unshift('');

        if (this.structure_id != null)
            this.loadStructure();

        var questions = $(this.$el).find('.fa-circle-question');

        var tt = new bootstrap.Tooltip(questions[0], {
            trigger: 'hover',
            placement: 'top',
            title: function() {
                return $(questions[0]).attr('title');
            }
        });        

        this.$emit('created');

        this.$refs.structVuln.focus();
    },
    methods: {
        loadStructure: function () {
            var me = this;

            $.get('GetStructure?structureID=' + this.structure_id + '&_t=' + (new Date()).getTime(), function (data) {
                me.structure_name = data.structure_name;
                me.vuln = data.vulnerability;
            });
        },
        parseVulnerability: function() {
            if(this.struct_vuln_text) {
                var lines = this.struct_vuln_text.split('\n');            
                if(lines.length == 4) {
                    this.vuln = _.trim(lines[1].substring(_.indexOf(lines[1], ':') + 1)).replace(":", "")
                    this.next_vuln = _.trim(lines[2].substring(_.indexOf(lines[2], ':') + 1)).replace(":", "")
                    this.next_vuln_date = _.trim(lines[3].substring(_.indexOf(lines[3], ':') + 1))
                }
            }
            else {
                this.vuln = null;
                this.next_vuln = null;
                this.next_vuln_date = null;
            }
        },        
        addVuln: function () {

            var self = this;

            var token = this.$root.$data.token;
            var header = this.$root.$data.header;
            var ajaxHeaders = {};
            ajaxHeaders[header] = token;

            this.showProcessing = true;

            var next_vuln_iso = ''
            if(this.next_vuln_date)
                next_vuln_iso = moment.utc(this.next_vuln_date, 'YYYY.MM.DD HH:mm').toISOString()

            $.ajax({
                cache: false,
                type: 'POST',
                url: "SaveStructureVulnerability",
                data: { structureID: this.structure_id, vulnerability: this.vuln, nextVulnerability: this.next_vuln, nextVulnerabilityDate: next_vuln_iso },
                dataType: "json",
                headers: ajaxHeaders
            }).done(function (data) {

                if (data.success) {
                    toastr.success('Vulnerability set successfully!')
                    self.$emit('vuln-modified');
                }
            });
        }
    }
}