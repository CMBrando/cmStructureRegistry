export default {
    template: '#structure-review',
    props: ['structure_id', 'structure_name'],
    data: function () {
        return {
        };
    },
    mounted: function () {
        this.$emit('created');
    },
    methods: {
        cancelReview: function () {
            this.$emit('review-canceled');
        },
        reviewStructure: function () {

            var self = this;

            var token = this.$root.$data.token;
            var header = this.$root.$data.header;
            var ajaxHeaders = {};
            ajaxHeaders[header] = token;

            $.ajax({
                cache: false,
                type: 'POST',
                url: "ReviewStructure",
                data: { structureID: this.structure_id },
                dataType: "json",
                headers: ajaxHeaders
            }).done(function (data) {

                if (data.success) {

                    if (toastr != null) {
                        toastr.success('Structure Marked as Reviewed.');
                    }
                    
                    self.$emit('structure-reviewed');
                }
            });
        }
    }
}