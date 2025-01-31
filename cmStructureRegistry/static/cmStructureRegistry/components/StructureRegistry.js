export default {
    template: '#structure-component',
    data: function () {
        return {
            show: false,
            sort: { property: "structure_name", direction: "asc" },
            structures: [],
            structures_flag: [],
            search: '',
            region_id: null
        };
    },
    props: ['type', 'refresh_key', 'admin', 'add', 'edit', 'add_timer'],
    mounted: function () {

        var query = window.location.search;
        var url = new URLSearchParams(query);
        var srch = url.get('s');
        if (srch !== null)
            this.search = srch;

        this.loadData();
    },
    watch: {
        sort: {
            deep: true,
            handler: function () {
                this.applySort();
            }
        },
        structures: {
            deep: true,
            handler: function () {

            }
        },
        refresh_key: function () {
            this.loadData();
        }
    },
    methods: {
        loadData: function () {

            //this.search = $(this.$el).find('.search-text').val();

            var me = this;

            var regId = this.region_id == null ? 0 : this.region_id;

            $.get('RegistryRead?term=' + encodeURIComponent(this.search) + '&regionId=' + regId, function (data) {

                me.structures = [];

                _.each(data, function (item) {

                    if (item.fit_json != null)
                        item.fit = JSON.parse(item.fit_json);
                    else
                        item.fit = {};

                    me.structures.push(item);
                    me.structures_flag.push({ val: false });
                });

                me.show = true;
                me.initTooltips();
                me.applySort(); // change the sorting if any
            });
        },
        regionSelected: function (region) {
            this.region_id = region.id;
            this.loadData();
        },
        formatDate: function (date) {
            if (date != null)
                return moment.utc(date).format('YYYY-MM-DD HH:mm');
            else
                return '';
        },
        addCommas: function (num) {
            return numeral(num).format('0,0');
        },
        getStatus: function (type, date) {
            if (type != null && date != null)
                return type + ' - ' + moment.utc(date).fromNow();
            else
                return '';
        },
        isSortProp: function (prop) {
            return (this.sort.property == prop);
        },
        showSortIcon: function (prop, dir) {
            return (this.sort.property == prop && this.sort.direction == dir);
        },
        toggleSort: function (prop) {
            if (this.sort.property == prop) {
                if (this.sort.direction == 'asc')
                    this.sort.direction = 'desc';
                else
                    this.sort.direction = 'asc';
            }
            else // switching properties so set and set to default asc
            {
                this.sort.property = prop;
                this.sort.direction = 'asc';
            }
        },
        toggleChild: function (index) {
            this.structures_flag[index].val = !this.structures_flag[index].val;
        },
        applySort: function () {

            var res = _.orderBy(this.structures, [this.sort.property], [this.sort.direction])
            this.structures = res;

            // reset all to hidden
            _.each(this.structures_flag, function (f) {
                f.val = false;
            });

            this.initTooltips();
        },
        onSubmit: function() {
           // dummy method
        },
        modifyFit: function (index) {
            this.$emit('edit-fit', this.structures[index].structure_id);
        },
        modifyVuln: function (index) {
            this.$emit('edit-vulnerability', this.structures[index].structure_id);
        },
        addTimer: function (index) {
            this.$emit('add-timer', this.structures[index].structure_id);
        },
        removeStructure: function (index) {
            this.$emit('remove-structure', this.structures[index].structure_id, this.structures[index].structure_name);
        },
        addStructure: function () {
            this.$emit('add-structure');
        },
        editStructure: function (index) {
            this.$emit('edit-structure', this.structures[index].structure_id);
        },
        initTooltips: function () {

            var that = this;

            this.$nextTick(function () {

                $(that.$el).find('.updated-tooltip').each(function(index, el) {
                    var tt = new bootstrap.Tooltip(el, {
                        trigger: 'hover',
                        placement: 'top',
                        title: function() {
                            return $(el).attr('updated');
                        }
                    })
                });

                $(that.$el).find('.status-tooltip').each(function(index, el) {

                    var tt = new bootstrap.Tooltip(el, {
                        trigger: 'hover',
                        placement: 'top',
                        title: 'Loading...'
                    })

                    el.addEventListener('shown.bs.tooltip', function () {

                        const innerEl = document.querySelector('.tooltip.show .tooltip-inner');

                        if(innerEl) {
                            var dt = moment.utc($(el).attr("timer"));
                            innerEl.textContent = moment().countdown(dt).toString();

                            // update every second while shown
                            const intervalId = setInterval(() => {
                                dt = moment.utc($(el).attr("timer"));
                                if(innerEl) // may have been remove from DOM
                                    innerEl.textContent = moment().countdown(dt).toString();
                            }, 1000);
                        
                            // Clear the interval when the tooltip is hidden
                            el.addEventListener('hide.bs.tooltip', function handleHide() {
                            clearInterval(intervalId);
                            el.removeEventListener('hide.bs.tooltip', handleHide);
                            });
                        }
                    
                    });

                });
            });            
        }
    }
}














