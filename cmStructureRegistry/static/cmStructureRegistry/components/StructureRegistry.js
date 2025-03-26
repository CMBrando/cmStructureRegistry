export default {
    template: '#structure-component',
    data: function () {
        return {
            show: false,
            sort: { property: "structure_name", direction: "asc" },
            structures: [],
            structures_flag: [],
            selUniverse: [],
            selCorp: [],
            selStructure: [],
            staging_system_id: null
        };
    },
    props: ['type', 'refresh_key', 'admin', 'add', 'edit', 'add_timer', 'stagingSystem'],
    mounted: function () {

        var query = window.location.search;
        var url = new URLSearchParams(query);

        var structId = url.get('sid');
        var structName = url.get('sname');
        
        if (structId !== null)
            this.selStructure.push({id: parseInt(structId), name: structName})

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

            var me = this;

            var universe = _.map(this.selUniverse, 'id').join(',')
            var corp = _.map(this.selCorp, 'id').join(',')
            var struct = _.map(this.selStructure, 'id').join(',')

            var url = '';
            if(this.staging_system_id)
                url = 'RegistryRead?staging_system=' + this.staging_system_id + '&universe=' + universe + '&corp=' + corp + '&structure=' + struct;
            else
                url = 'RegistryRead?universe=' + universe + '&corp=' + corp + '&structure=' + struct;

            $.get(url, function (data) {

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
        universeSelected: function(item) {
            if(item && item.id) {
                var index = _.findIndex(this.selUniverse, function (t) { return t.id === item.id; });

                if(index === -1) {
                    this.selUniverse.push(item);
                    this.loadData();
                }
            }
        },     
        corpSelected: function(item) {
            if(item && item.id) {
                var index = _.findIndex(this.selCorp, function (t) { return t.id === item.id; });

                if(index === -1) {
                    this.selCorp.push(item);
                    this.loadData();
                }
            }
        },     
        structureSelected: function(item) {
            if(item && item.id) {            
                var index = _.findIndex(this.selStructure, function (t) { return t.id === item.id; });

                if(index === -1) {
                    this.selStructure.push(item);
                    this.loadData();
                }
            }
        },
        removeUniverseInput: function(id) {
            var index = _.findIndex(this.selUniverse, function (t) { return t.id === id; });
            if(index > -1) {
                this.selUniverse.splice(index, 1)
                this.loadData();
            }
        },
        removeCorpInput: function(id) {
            var index = _.findIndex(this.selCorp, function (t) { return t.id === id; });
            if(index > -1) {
                this.selCorp.splice(index, 1)
                this.loadData();
            }
        },
        removeStructureInput: function(id) {
            var index = _.findIndex(this.selStructure, function (t) { return t.id === id; });
            if(index > -1) {
                this.selStructure.splice(index, 1)
                this.loadData()
            }
        },
        stagingSystemChanged: function(item) {
            this.staging_system_id = item.id;
            this.loadData()
        },        
        formatDate: function (date) {
            if (date != null)
                return moment.utc(date).format('YYYY-MM-DD HH:mm');
            else
                return '';
        },
        formatFloat: function (number) {
            return numeral(number).format('0.0')
        },          
        addCommas: function (num) {
            return numeral(num).format('0,0');
        },
        distanceText: function(struct) {
            if(struct.jumps) {
                var distance = this.formatFloat(struct.distance);
                return `${distance} ly (${struct.jumps} jp)`;
            }
            else
                return ''
        },
        getReviewTooltip: function(struct) {

            if(struct.vulnerability_updated && struct.fit_updated && this.formatDate(struct.vulnerability_updated) == this.formatDate(struct.fit_updated))
                return 'All Reviewed by: ' + struct.vulnerability_updated_by;

            var result = '';

            if(struct.vulnerability_updated)
                result = 'Vuln: <i>' + this.formatDate(struct.vulnerability_updated) + '</i> by ' + struct.vulnerability_updated_by;

            if(struct.vulnerability_updated && struct.fit_updated)
                result += '<br/>'

            if(struct.fit_updated)
                result += 'Fit: <i>' + this.formatDate(struct.fit_updated) + '</i> by ' + struct.fit_updated_by;

            return result;
        },
        getVulnTooltip: function(struct) {
                
                if(struct.next_vulnerability)
                    return 'Next Vuln: ' + struct.next_vulnerability + '<br/>Date: ' + this.formatDate(struct.next_vulnerability_date);
                
                return '';
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
        loadReviewStructure: function (index) {
            this.$emit('set-review', this.structures[index]);
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
                        html: true,
                        placement: 'top',
                        title: function() {
                            return $(el).attr('updated');
                        }
                    })
                });

                $(that.$el).find('.vuln-tooltip').each(function(index, el) {
                    var tt = new bootstrap.Tooltip(el, {
                        trigger: 'hover',
                        html: true,
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














