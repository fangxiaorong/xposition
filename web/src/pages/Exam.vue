<template>
  <div>
    <v-container grid-list-xl fluid>
      <v-layout row wrap>
        <v-flex lg3>
          <v-card>
            <v-list>
              <v-list-tile v-for="item in exams" :key="item.id" @click="pathSelected(item)">
                <v-list-tile-action>
                  <v-btn icon ripple @click.stop="examActive(item)">
                    <v-icon color="primary">{{ item.id === active_exam_id ? 'lock' : (item.state === 2 ? 'history' : 'lock_open') }}</v-icon>
                  </v-btn>
                </v-list-tile-action>

                <v-list-tile-content>
                  <v-list-tile-title v-text="item.name"></v-list-tile-title>
                </v-list-tile-content>

                <v-list-tile-avatar v-if="item.state === 1">
                  <v-btn icon ripple @click.stop="editExam(item)">
                    <v-icon color="grey lighten-1">edit</v-icon>
                  </v-btn>
                </v-list-tile-avatar>

              </v-list-tile>
              <v-dialog v-model="dialog" max-width="800px">
                <v-btn slot="activator" color="primary" dark class="mb-2">新增</v-btn>
                <v-card>
                  <v-card-title>
                    <span class="headline">新建考试</span>
                  </v-card-title>
                  <v-card-text>
                    <v-container grid-list-md>
                      <v-layout wrap>
                        <!-- <v-text-field v-model="examname" label="考试名称"></v-text-field> -->
                        <v-flex xs12 sm12 md12>
                          <v-text-field v-model="editedItem.name" label="考试名称" :readonly="editedItem.id>=0"></v-text-field>
                        </v-flex>
                        <!-- <v-flex xs12 sm12 md3>
                          <v-text-field v-model="editedItem.starttime" label="开始时间(1999-10-10 12:12:12)"></v-text-field>
                        </v-flex>
                        <v-flex xs12 sm12 md3>
                          <v-text-field v-model="editedItem.endtime" label="结束时间(1999-10-10 12:12:12)"></v-text-field>
                        </v-flex> -->
                        <v-flex xs12 sm6 md3>
                          <v-text-field v-model="editedItem.score1" label="优秀"></v-text-field>
                        </v-flex>
                        <v-flex xs12 sm6 md3>
                          <v-text-field v-model="editedItem.score2" label="良好"></v-text-field>
                        </v-flex>
                        <v-flex xs12 sm6 md3>
                          <v-text-field v-model="editedItem.score3" label="及格"></v-text-field>
                        </v-flex>
                        <v-flex xs12 sm6 md3>
                          <v-text-field v-model="editedItem.score4" label="得分"></v-text-field>
                        </v-flex>

                        <v-flex xs12 sm12 md6>
                         <el-date-picker v-model="editedItem.starttime" type="datetime" placeholder="选择日期时间" />
                        </v-flex>
                        <v-flex xs12 sm12 md6>
                          <el-date-picker v-model="editedItem.endtime" type="datetime" placeholder="选择日期时间" />
                        </v-flex>

                      </v-layout>
                    </v-container>
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
            <!-- <v-toolbar-title>{{ selected.name + '(&#60;=' + selected.level1 + '优秀 &#60;=' + selected.level2 + '良好 &#60;=' + selected.level3 + '及格 &#60;=' + selected.level4 + '得分)'}}</v-toolbar-title> -->
            <!--  + '(' + (selected.starttime === undefined ? '时间未设置' : (selected.starttime + '-' + selected.endtime)) + ')' -->
            <v-toolbar-title>{{ selected.name + ' -- [ 优秀(' + selected.score1 + ') 良好(' + selected.score2 + ') 及格(' + selected.score3 + ') 得分(' + selected.score4 + ') ]'}}</v-toolbar-title>
            <v-divider class="mx-2" inset vertical></v-divider>
            <v-spacer></v-spacer>
            <input type="file" name="importuser" @change="handleFileChange" v-show="selected.state === 1">
          </v-toolbar>
          <v-data-table :headers="headers" :items="desserts" hide-actions>
            <template slot="items" slot-scope="props">
              <td>{{ props.item.exam_id }}</td>
              <td v-if="selected.state === 1">
                <v-select :items="lines" v-model="props.item.line_id" item-text="name" item-value="id"></v-select>
              </td>
              <td v-else>{{ props.item.line ? props.item.line.name : props.item.line_id }}</td>
              <td>{{ props.item.username }}</td>
              <td>{{ props.item.device_id }}</td>
              <td>{{ props.item.departname }}</td>
              <td>
              </td>
            </template>
            <template slot="no-data">
              <div></div>
            </template>
          </v-data-table>
          <div class="text-xs-right">
            <v-btn color="primary" @click="saveExamUser" v-show="desserts.length > 0 && selected.state === 1">保存</v-btn>
          </div>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import jschardet from 'jschardet';

export default {
  data: () => ({
    selected: undefined,
    exams: [],
    active_exam_id: -1,
    lines: [],
    dialog: false,
    headers: [
      { text: '考试号', value: 'name', sortable: false, align: 'left' },
      { text: '路线号', value: 'calories', sortable: false },
      { text: '姓名', value: 'fat', sortable: false },
      { text: '设备号', value: 'carbs', sortable: false },
      { text: '所属单位', value: 'carbs', sortable: false },
    ],
    desserts: [],
    editedIndex: -1,
    editedItem: {
      id: -1,
      name: '',
      score1: 0,
      score2: 0,
      score3: 0,
      score4: 0,
      starttime: '',
      endtime: ''
    },
    defaultItem: {
      id: -1,
      name: '',
      score1: 0,
      score2: 0,
      score3: 0,
      score4: 0,
      starttime: '',
      endtime: ''
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
      let that = this;
      that.axios.all([that.axios.get('/api/admin/examline/list?valid=1'), that.axios.get('/api/admin/exams')]).then(that.axios.spread((lines_resp, exams_resp) => {
        console.log(lines_resp);
        console.log(exams_resp);

        if (exams_resp.data.state === 1) {
          that.exams = exams_resp.data.exams;
          that.active_exam_id = exams_resp.data.active_exam_id;
        }

        if (lines_resp.data.state === 1) {
          // let lines = {};
          // lines_resp.data.exam_line.forEach((line) => {
          //   lines[line.id] = line;
          // });
          that.lines = lines_resp.data.exam_line;
        }
      }));
    },
    close () {
      this.dialog = false;
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      }, 300);
    },
    newExam () {
      if (this.editedItem.name.trim() === '') {
        alert('名字不能为空！');
      } else if (this.editedItem.starttime.trim() === '' || this.editedItem.endtime.trim() === '') {
        alert('起止时间必须设置');
      } else {
        let data = 'name=' + encodeURI(this.editedItem.name.trim()) +
                   '&score1=' + this.editedItem.score1 +
                   '&score2=' + this.editedItem.score2 + 
                   '&score3=' + this.editedItem.score3 +
                   '&score4=' + this.editedItem.score4 +
                   '&starttime=' + this.editedItem.starttime +
                   '&endtime=' + this.editedItem.endtime;
        if (this.editedIndex > -1) {
          // Object.assign(this.desserts[this.editedIndex], this.editedItem);
          data = data + '&exam_id=' + this.editedItem.id;
          this.axios.post('/api/admin/exam', data).then((response) => {
            console.log(response);
            if (response.data.state === 1) {
              this.initialize();
              this.close();
            } else {
              window.alert(response.data.message);
            }
          });
        } else {
          this.axios.post('/api/admin/exam', data).then((response) => {
            console.log(response);
            if (response.data.state === 1) {
              this.initialize();
              this.close();
            } else {
              window.alert(response.data.message);
            }
          });
        }
      }
    },
    examActive (item) {
      this.axios.post('/api/admin/exam', 'exam_id=' + item.id).then((response) => {
        console.log(response.data);
        if (response.data.state === 1) {
          this.active_exam_id = item.id;
          this.selected.state = 2;
        } else {
          alert(response.data.message);
        }
      });
    },
    editExam (item) {
      this.editedIndex = this.exams.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog = true;
    },
    handleFileChange (event) {
      if (typeof (FileReader) !== 'undefined') {
        let that = this;
        let reader = new FileReader();
        reader.readAsArrayBuffer(event.target.files[0]);
        reader.onload = function (evt) {
          let data =  new Uint8Array(evt.target.result);
          let characterTestStr = null;
          for (let index in data) {
            if (index <= 100) {
              characterTestStr += String.fromCharCode(data[index]);
            } else {
              break;
            }
          }
          let codepage = jschardet.detect(characterTestStr.substring(0, 1000)).encoding;
          if (codepage === 'GB2312' || codepage === 'GB18030') {
            codepage = 'GB18030';
          } else if (!(codepage === 'ascii' || codepage === 'UTF-8' || codepage === 'UTF-16BE' || codepage === 'UTF-16LE')) {
            alert('不支持的编码格式:' + codepage + ';你只能使用UTF-8或GB18030(GB2320,GBK)编码格式文件');
            return;
          }

          data = new TextDecoder(codepage).decode(data).split('\r\n');
          let result = [];
          console.log(that.selected);
          data.forEach(item => {
            let tmp = item.split(',');
            if (tmp.length >= 3 && tmp[0].trim() !== '' && tmp[1].trim() !== '' && tmp[2].trim() !== '') {
              result.push({
                exam_id: that.selected.id,
                line_id: that.lines[Math.floor(Math.random() * that.lines.length)].id,
                username: tmp[0],
                device_id: tmp[1],
                departname: tmp[2],
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
    getExamUser () {
      this.axios.get('/api/admin/examuser/list/' + this.selected.id).then((response) => {
        console.log(response);
        if (response.data.state === 1) {
          this.desserts = response.data.users;
        }
      });
    },
    saveExamUser () {
      this.axios.post('/api/admin/examuser/list/' + this.selected.id, 'exam_users=' + encodeURI(JSON.stringify(this.desserts))).then((response) => {
        if (response.data.state === 1) {
          window.alert('保存成功');
        } else {
          window.alert(response.data.message);
        }
      });
    }
  }
};
</script>
