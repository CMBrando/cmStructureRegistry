﻿export default {
    template: '#vue-autocomplete',
    props: {
        items: {
            type: Array,
            required: false,
            default: () => []
        },
        isAsync: {
            type: Boolean,
            required: false,
            default: false
        },
        minChars: {
            type: Number,
            required: false,
            default: 0
        },
        placeholder: {
            type: String,
            required: false,
            default: 'Search...'
        },
        enableClearOption: {
            type: Boolean,
            required: false,
            default: false
        },
        initSystem: {
            type: String,
            required: false,
            default: ''
        }
    },
    data() {
        return {
            isOpen: false,
            results: [],
            search: this.initSystem,
            isLoading: false,
            arrowCounter: -1,
            showClear: this.enableClearOption && this.search
        };
    },
    watch: {
        initSystem: function() {
            this.search = this.initSystem;
            this.filterByUrl();
        }
    },
    methods: {
        onChange() {
            // Let's warn the parent that a change was made
            this.$emit("input", this.search);

            var $that = this;

            // Is the data given by an outside ajax request?
            if (this.search.length >= this.minChars) {

                if (this.isAsync) {
                    this.isOpen = true;
                    this.isLoading = true;
                    this.filterByUrl();

                } else {
                    // Let's search our flat array
                    this.filterResults();
                    this.isOpen = true;
                }
            }
        },
        delayOnChange: _.debounce(function () {
            this.onChange();
        }, 300),
        filterResults() {
            // first uncapitalize all the things
            this.results = this.items.filter(item => {
                return item.toLowerCase().indexOf(this.search.toLowerCase()) > -1;
            });
        },
        filterByUrl() {
            var that = this;
            //$.getJSON('../Ship/SearchSolarSystem?query=' + this.search + '&_t=' + (new Date()).getTime(), null, function (data) {
            //    //that.results = _.map(data, function (d) { return d.name; });
            //    that.results = data;
            //    that.isLoading = false;
            //    that.arrowCounter = -1;
            //});
            fetch('SearchSolarSystems?query=' + this.search)
                .then(resp => {
                    return resp.json()
                })
                .then(data => {
                    that.results = data;
                    that.isLoading = false;
                    that.arrowCounter = -1;
                })
        },
        setResult(result) {
            this.search = result.name;
            this.isOpen = false;

            this.$emit('item-selected', result);
            this.arrowCounter = -1;
        },
        onArrowDown(evt) {
            if (this.arrowCounter < this.results.length) {
                this.arrowCounter = this.arrowCounter + 1;
            }

            var that = this;
            this.$nextTick(function () {
                that.$refs.resultInput[that.arrowCounter].scrollIntoView(false);
            });
        },
        onArrowUp() {
            if (this.arrowCounter > 0) {
                this.arrowCounter = this.arrowCounter - 1;
            }

            var that = this;
            this.$nextTick(function () {
                that.$refs.resultInput[that.arrowCounter].scrollIntoView(false);
            });
        },
        onEnter() {
            // select first one if only result
            if(this.arrowCounter == -1 && this.results.length == 1) {
                this.search = this.results[0].name;
                this.isOpen = false;               
                this.$emit('item-selected', this.results[0]);                
            }
            else if(this.arrowCounter > -1) {
                this.search = this.results[this.arrowCounter].name;
                this.isOpen = false;
    
                this.$emit('item-selected', this.results[this.arrowCounter]);
                this.arrowCounter = -1;    
            }  
        },
        onBlur: function () {
            var $that = this;
            setTimeout(function() {
                if ($that.search === '')
                    $that.$emit('item-selected', { id: null, name: null });
    
                $that.isOpen = false;    
            }, 200)
        },
        clearSelection: function () {
            this.showClear = false;
            this.search = '';
            this.$emit('item-selected', { id: null, name: '', name: null });
        }
    },
    watch: {
        items: function (val, oldValue) {
            // actually compare them
            if (val.length !== oldValue.length) {
                this.results = val;
                this.isLoading = false;
            }
        },
        search: function() {
            if(this.search)
                this.showClear = true;
            else
                this.showClear = false;
        }
    },
    mounted() {
        
    },
    destroyed() {
        
    }
}