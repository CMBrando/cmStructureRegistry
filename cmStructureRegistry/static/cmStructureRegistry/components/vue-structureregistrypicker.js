export default {
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
        initStructure: {
            type: String,
            required: false,
            default: ''
        }
    },
    data() {
        return {
            isOpen: false,
            results: [],
            search: this.initStructure,
            isLoading: false,
            arrowCounter: -1,
            showClear: false
        };
    },
    watch: {
        items: function (val, oldValue) {
            // actually compare them
            if (val.length !== oldValue.length) {
                this.results = val;
                this.isLoading = false;
            }
        },
        initStructure: function() {

            var that = this;

            if(this.initStructure)
            {
                this.search = this.initStructure;

                if(this.isAsync)
                    this.filterByUrl();
                else
                    this.filterResults();

                // find better way to do this
                setTimeout(function() {
                    that.setResult(that.results[0]);
                }, 500)
            }
        }
    },
    methods: {
        onChange() {
            this.$emit("input", this.search);

            var $that = this;

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
            fetch('SearchRegistry?query=' + this.search)
                .then(resp => {
                    return resp.json()
                })
                .then(data => {
                    //that.results = data;
                    that.results = _.map(data, function (d) { return { id: d.structure_id, name: d.structure_name }; });
                    that.isLoading = false;
                    that.arrowCounter = -1;
                })
        },
        setResult(result) {

            if(result) {
                this.search = result.name;
                this.$emit('item-selected', result);
            }

            this.isOpen = false;
            this.showClear = true;
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
            this.search = this.results[this.arrowCounter].name;
            this.isOpen = false;
            this.showClear = true;

            this.$emit('item-selected', this.results[this.arrowCounter]);
            this.arrowCounter = -1;
        },
        onBlur: function () {
            if (this.search === '')
                this.$emit('item-selected', { id: null, name: null });
        },
        clearSelection: function () {
            this.showClear = false;
            this.search = '';
            this.$emit('item-selected', { id: null, name: '', name: null });
        },
        handleClickOutside(evt) {
            if (!this.$el.contains(evt.target)) {
                this.isOpen = false;
                this.arrowCounter = -1;
            }
        }
    },
    mounted() {
        document.addEventListener("click", this.handleClickOutside);
    },
    destroyed() {
        document.removeEventListener("click", this.handleClickOutside);
    }
}