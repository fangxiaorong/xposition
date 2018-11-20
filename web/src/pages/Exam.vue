<template>
  <div>
    <v-container grid-list-xl fluid>
      <v-layout row wrap>
        <v-flex lg3>
          <v-card>
            <v-list>
              <v-list-tile v-for="item in exams" :key="item.id" @click="pathSelected(item)">
                <v-list-tile-action>
                  <v-checkbox off-icon="bookmark" on-icon="bookmark_border">star</v-checkbox>
                </v-list-tile-action>

                <v-list-tile-content>
                  <v-list-tile-title v-text="item.name"></v-list-tile-title>
                </v-list-tile-content>
              </v-list-tile>
              <!-- <div class="text-xs-center">
                <v-btn flat icon color="pink"><v-icon>add_circle</v-icon></v-btn>
              </div> -->
              <v-dialog v-model="dialog" max-width="800px">
                <v-btn slot="activator" color="primary" dark class="mb-2">新增</v-btn>
                <v-card>
                  <v-card-title>
                    <span class="headline">新建考试</span>
                  </v-card-title>
                  <v-card-text>
                    <v-text-field v-model="examname" label="考试名称"></v-text-field>
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" flat @click.native="close">取消</v-btn>
                    <v-btn color="blue darken-1" flat @click.native="newExam">保存</v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </v-list>
          </v-card>
          
        </v-flex>
        <v-flex lg9 v-if="selected">
          <v-toolbar flat color="white">
            <v-toolbar-title>{{ selected.name }}</v-toolbar-title>
            <v-divider class="mx-2" inset vertical></v-divider>
            <v-spacer></v-spacer>
            <input type="file" name="importuser" @change="handleFileChange">
          </v-toolbar>
          <v-data-table :headers="headers" :items="desserts" hide-actions>
            <template slot="items" slot-scope="props">
              <td>{{ props.item.exam_id }}</td>
              <td><v-select :items="exam_lines" v-model="props.item.line_id"></v-select></td>
              <!-- <td>{{ props.item.line_id }}</td> -->
              <td>{{ props.item.username }}</td>
              <td>{{ props.item.device_id }}</td>
              <td>
              </td>
            </template>
          </v-data-table>
          <div class="text-xs-right">
            <v-btn color="primary" @click="saveExamUser" v-show="desserts.length > 0">保存</v-btn>
          </div>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
export default {
  data: () => ({
    selected: undefined,
    exams: [],
    examname: '',
    exam_lines: ['1', '2'],
    dialog: false,
    headers: [
      { text: '考试号', value: 'name', sortable: false, align: 'left' },
      { text: '路线号', value: 'calories', sortable: false },
      { text: '姓名', value: 'fat', sortable: false },
      { text: '设备号', value: 'carbs', sortable: false },
    ],
    desserts: [],
    editedIndex: -1,
    editedItem: {
      name: '',
      calories: 0,
      fat: 0,
      carbs: 0,
      protein: 0
    },
    defaultItem: {
      name: '',
      calories: 0,
      fat: 0,
      carbs: 0,
      protein: 0
    }
  }),
  computed: {
    formTitle () {
      return this.editedIndex === -1 ? 'New Item' : 'Edit Item';
    },
  },
  watch: {
    dialog (val) {
      val || this.close();
    },
  },
  created () {
    this.initialize();
  },
  methods: {
    initialize () {
      this.axios.get('/api/admin/exams').then((response) => {
        this.exams = response.data.exams;
      });
    },

    getExamUser () {
      this.axios.get('/api/admin/examuser/list/' + this.selected.id).then((response) => {
        console.log(response);
        if (response.data.state === 1) {
          this.desserts = response.data.users;
        }
      });
    },

    editItem (item) {
      this.editedIndex = this.desserts.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog = true;
    },

    deleteItem (item) {
      const index = this.desserts.indexOf(item);
      confirm('Are you sure you want to delete this item?') && this.desserts.splice(index, 1);
    },

    close () {
      this.dialog = false;
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      }, 300);
    },

    newExam () {
      if (this.examname.trim() === '') {
        alert('名字不能为空！');
      } else {
        if (this.editedIndex > -1) {
          Object.assign(this.desserts[this.editedIndex], this.editedItem);
        } else {
          // this.desserts.push(this.editedItem);
          this.axios.post('/api/admin/exam', 'name=' + this.examname.trim()).then((response) => {
            console.log(response);
            if (response.data.state === 1) {
              this.initialize();
            }
          });
        }
        this.close();
      }
    },
    handleFileChange (event) {
      if (typeof (FileReader) !== 'undefined') {
        let that = this;
        let reader = new FileReader();
        reader.readAsText(event.target.files[0]);
        reader.onload = function (evt) {
          let data = evt.target.result.split('\r\n');
          let result = [];
          console.log(that.selected);
          data.forEach(item => {
            let tmp = item.split(',');
            if (tmp.length >= 2 && tmp[0].trim() !== '' && tmp[1].trim() !== '') {
              result.push({
                exam_id: that.selected.id,
                line_id: '1',
                username: tmp[0],
                device_id: tmp[1],
              });
            }
            that.desserts = result;
          });
        };
      } else {
        alert('IE9及以下浏览器不支持，请使用Chrome或Firefox浏览器');
      }
    },
    pathSelected (item) {
      let fileSelect = this.$el.querySelector('input[type=file]');
      if (fileSelect) {
        fileSelect.value = '';
      }
      this.selected = item;
      this.getExamUser();
    },
    saveExamUser () {
      //
    }
  }
};
</script>
