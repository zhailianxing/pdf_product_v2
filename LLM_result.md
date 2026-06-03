## Prompt

这是一个金属材料的材质报告，对其化学成分和力学性能是否符合标准做出判断

## Overview

|          | 3-VL-8B-Instruct                                             | 3-VL-32B-Instruct                                   | 3-VL-235B-Instruct                                           | 3-VL-Flash                  | 3-VL-Plus                                 |
| -------- | ------------------------------------------------------------ | --------------------------------------------------- | ------------------------------------------------------------ | --------------------------- | ----------------------------------------- |
| VDV      | √*（硬度和冲击功识别混合）                                   | √                                                   | √                                                            | ×（范围抓不出，炉号抓不出） | √*（温度和冲击功识别混合/炉号识别不稳定） |
| 迪宝     | √                                                            | √                                                   |                                                              |                             | √                                         |
| 轩诺     | √*（delta Fe要求没识别出来；S元素不合格没判断出来）          | √*（delta Fe要求没识别出来；S元素不合格没判断出来） | √*（delta Fe识别为Fe,可以识别到数值了，且S不合格也判断出来了） |                             | √*（S元素不合格没判断出来）               |
| 巨力     | ×（化学成分要求只能识别到单边）                              | ×（力学性能引用了原标准，而不是报告里写的）         | ×（力学性能识别错误）                                        |                             | ×（化学成分力学性能胡说八道）             |
| 中山高纬 | √*（少识别了qWCD）                                           | √                                                   |                                                              |                             |                                           |
| R470     | √                                                            | √                                                   |                                                              |                             |                                           |
| 博坦     | ×（化学成分要求只能识别到单边）                              | √*（S元素范围完全不对）                             | √*（S元素范围完全不对，引用原标准）                          |                             |                                           |
| 总体评价 | 有时候会把数值为空白的如硬度要求识别为旁边的数值；对范围为max/min的只能识别单边要求 | 修复了8B只能识别单边的问题，但是幻觉比8B严重        | 幻觉有点严重                                                 | 不适用                      | 比flash强点儿                             |

## **文件汇总**

### VDV

C3 威地威.pdf

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NGIxMzU5ZDZmMjkwNjM3ZTVmZmJkZGJjMzEzYzMxYzlfQndEeU5PS3RxbEgwU3lndVBSYkpZa280djdwT2cyeXRfVG9rZW46QlFzNWJCRkVJb2ZhV0t4amR5cGNkNWhKbnZlXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 迪宝

F3 迪宝.pdf

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=YWQ0OTYwNWZkZTIxNDJmZDIyN2U0ZTMwMmU5OTEzYzVfTE1xOWQxZUJuZnJDMFV0VkY1MWpDNWxWRE1YNWlxbElfVG9rZW46V2dYaWJ5NVV6bzhiMVJ4eVlUcWMwRHJnbkVlXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 轩诺

F1 轩诺.pdf

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=MTgxMTI1MWU3M2M4YTU2ZDA0YWM2ZDdkMjMyZWRmZWRfWlVFWkpIaWk3eXF3ZjhzZ1NEUXhrcm50YkRDNW9PVjlfVG9rZW46T213UWJDamx4bzZ5ZDZ4cHJQdWNQM21vbnpZXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 巨力

C3 巨力.pdf

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=MDU0NDY2OWQ3Mzk3Y2FiOGIyZTYzZTBlY2NlZGQ0YWVfMU1iUmxLVDFnMW9wYWpvZDhlUDYxUXpaUHJYVEIzRHJfVG9rZW46QmFleWJjUEJxb1d2d3h4NkwxSGN0QVBNblZjXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 中山高纬

高纬材质证明.pdf

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NjUwMjRhMWI5ODQxODFhZTA1M2UwNGUwMzk1MmNmOWFfRkh1cnZMQ00xeEs0cmF4anVuOVJoMUI1RjJSWVAxb3pfVG9rZW46R0dZdmJVWm9Pb085VkZ4Vmh0a2NWU3A5bmRWXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### R470

R470材质证明.pdf

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=ZWQ3MjU5YzU0YWNlZWU2ZWNlYTM1ZDA5YjFjMzUzNjZfMlM1ZnNjSGNmMkhkRzVmaWdxRExLM2VkUk1XMk9ISVJfVG9rZW46QXladmJPbnkwb3RzVlR4TVZ2WmNPZWM0blZoXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NjI5YmQ4ZWRjNTcwMmIyNmJmMmYzZjMyNTIzNTMyMTdfNks1R21ScGpDMlh6UVhlRHlDZlluSHo4ODNwSjF2Z1VfVG9rZW46UkhxYWI0WVVSbzBrdmR4c2pPWmNhN0JDbmNkXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 博坦

F1 博坦.pdf

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NGUyOTI5MmQwYWNiMDBkM2M0Yzk1YTM1NGVkZmYyNzFfVzZPNnlkQUQ0eXRNdGdqdk55VEM5amxnWkxCMDNZVEFfVG9rZW46VWw2SmJKcTlwb21FdGV4QjZNVGNkeEZLblpnXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

## Qwen3-VL-8B-Instruct

|          | 炉号是否能识别 | 化学/机械范围是否正确                           | 冲击功                                                       |
| -------- | -------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| VDV（1） | √              | ×（把一次冲击功测试数值当成机械性能硬度测试值） | √*（把其中一次测试的值当作对每次测试的要求，但平均值抓得出来） |
| VDV（2） | √              | ×（把一次冲击功测试数值当成机械性能硬度测试值） | √（抓得出平均值，也看得出三个试棒的分别测试值）              |
| VDV（3） | √              | ×（把一次冲击功测试数值当成机械性能硬度测试值） | √（抓得出平均值，也看得出三个试棒的分别测试值）              |
| 迪宝     | √              | √                                               | √                                                            |
| 轩诺     | √              | √*（铁素体含量没认出来）                        | √                                                            |
| 巨力     | √              | ×（化学成分范围只能识别到单边）                 | √（抓得出平均值，也看得出三个试棒的分别测试值）              |
| 中山高纬 | √              | √*（少识别了qWCD炉号的全部信息）                | 没要求                                                       |
| R470     | √              | √                                               | √                                                            |
| 博坦     | √              | ×（化学成分范围只能识别到单边）                 | 没要求                                                       |

### VDV

#### 第一次测试

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NDJkYWFiMmMzMjM4ZDNjMDllMWNlOTllMTFjOTFhNDVfVnV6bGszTXBDMHFxUjNiQ25BM1l4ZFpCV3NXZmtkNGpfVG9rZW46TkswMWJrc25ib0VOWW94NXBTdmMwTUxpblRQXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=ZDI3OTU5OTBkMGU0ZjNiMWVlZDllMmFjNTU4MGY4OWNfQmdtS3ozUmhsSnFDQWdWRFh3MjBlZHRwd2FQa0dDVDFfVG9rZW46V1I2OWJXZnZYb3BhTzZ4dzdMemNnN1liblVkXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

#### 再次测试

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NmI4NDQ5NzA1MWMzMzc1M2Y3MzU3MWYwOWI2MGNhZGFfdFlXVUNxTHNBbkt3NU1LZnNnVlR6V2ptNXZsWHJJSUdfVG9rZW46SnUxTWJXZmxKb3BlSmx4V0NGM2NNWjdxbnZiXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

#### 第三次测试

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=MjcyZGJkY2JlNjMzZTE5NTI4ZmI3ZjdkMTAzYjYyOWZfZHhPVXZhVkRlVU1VMGh4UVFmWGhvZ2l6Sk51b1h6TzFfVG9rZW46WmQ4NWJFMUExb2toRU14NHhmY2M4QWxwbnNyXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=MmNiOTc4YmIwMDBiNDQ4NmUxZjM1NTQ5ZTc5ZmRiMGRfemJ2eVFWUG12WlZZUnFTM1R3a0o0ODlGVmFyQ2ZEN1RfVG9rZW46UmoyVGJpNHdzb3Z6VWx4ZE1TYWNyYlZFbnZnXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 轩诺

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NDg3ZmI4NjQzMWEyYzZiM2ZjZjgxZTVlYTY4ZDM2NGJfaW50RW5UODd4UUZua1ZrUWxxNzd2YzFZdUpMdkFzOFhfVG9rZW46WDVLZWJvbHpDb0dhWTV4cDBYSGN5RDNhbnhlXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 巨力

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NmQyMTRjOTYzMTkyMzk5OGMwNzFiNmVmZDk5MGUzYjhfdWJXNUJPalpXZlBvVWJSR2VaTXJOSll3Rm9RZlhDbFpfVG9rZW46SWhpeWJsZGhEb2ZrOHd4OHFzNWNJdk1mbmpnXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 博坦

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=MjlhYTQyYzc1NTM4ODBmMzc0NjQ4MjViMDQ3MDQzYzRfQXdmWWNrblFDOGlXVFpaaTJid1NodGJmeFdXS0h3R1ZfVG9rZW46WXB3T2JWQVV4b21aajZ4MHgwTmNnNFhBbjRlXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

## Qwen3-VL-Flash

|      | 炉号是否能识别            | 化学/机械范围是否正确                                        | 冲击功                                   |
| ---- | ------------------------- | ------------------------------------------------------------ | ---------------------------------------- |
| VDV  | ×（把炉号识别为材质牌号） | 化学实测值抓的没问题，范围差很多；力学实测值（除了硬度）没问题，范围差很多 | 3次分别测试/平均数值抓的出，范围也抓的出 |

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=Y2E0ZDE2YjU3YWM4NWNlNTBkYWI0YzQxMzZkNGE1ZmRfTmlDTG92cGtGT2U4YTNkNkFtaFY5aGh1eVVUZGNkcGFfVG9rZW46TnBnT2JrOVFpb2NKcm54VkxZemNzSm5iblVnXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=YTExYjZiMDAxOWQ5N2NhM2Y0YzFhMmY3ZjhjNDkyODNfNEZ1NlBxTHdtWU5oaE16RG83NW9uT2ZoYlZTSGxnNGZfVG9rZW46TWV3RmJiZjRQb0haSDd4MURQZ2NVQzE3blZlXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

## Qwen3-VL-Plus

|      | 炉号是否能识别                                   | 化学/机械范围是否正确                                        | 冲击功                                       |
| ---- | ------------------------------------------------ | ------------------------------------------------------------ | -------------------------------------------- |
| VDV  | ×*（把炉号识别为材质牌号，后续追问识别出是炉号） | 化学范围和实测值都没问题；机械实测值也抓的出，冲击功要求抓成了右侧温度实测值 | 3次分别测试/平均数值抓的出，范围抓成右侧温度 |
| 迪宝 | √                                                | √                                                            | √                                            |
| 轩诺 | √                                                | √*（铁素体含量没认出来，S也没判断出来）                      | √                                            |
| 巨力 | √                                                | ×（最大值和实际值经常搞混，化学成分判断纯傻子，力学性能逮谁认谁） | ×（大傻子）                                  |

### VDV

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NzRhY2M2ZWZjMzMyNTFhYTUwNjJkNDBjMDUyNjgzOTRfS1hqbUhpSUFSWEZYYVpScklzclFSRkdYbTB2MmVtbmtfVG9rZW46TjY2amJGaHcxb0c1NXp4Y1R5SGNDcmQxbmZkXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 轩诺

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NGE3ZjkyNTA0ODM4MDUwNTM1YjExYzYxZjNlNDRmNWZfMFRUQlp0MDdGeHJOM2VQSFNUbDBsa3RVaktkbXZiSjBfVG9rZW46TzlpdmJRSXRob2k1N2Z4OHFacWNvQVZEbmViXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 巨力

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=ODRiNTE3ZmYwMzRmZTczNzRlMjE0ZGI1NzNiNjFjMmNfdHNBUHhPeUtJS3VRYXl5aGh3Q1d4eXF2QnJVbXhxRHBfVG9rZW46WHo1TWJlM0lDb2ZnUnN4RjlobWM1WnVabmhlXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=Nzk5ZWZkZmY1N2RhMmQwZTM3ZTkwZTVjMjY4ZDhiMjBfb2ppUk1LOG4yOXBoZWtHamk0bnVqUXhWNGZ0N2xTZ0RfVG9rZW46T05nOGJ6cVhRb0NVcVN4MXFoSWNFT1REbjVnXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=ZmMwMWRkMWMwYzE1ZDMzZTNmY2I0ZTVhMjI0N2M4NWZfcjNSQ0lsTERFNzYyZVdjVEVaUUhOcHNuZXV1V01qSkZfVG9rZW46Um9yTWJicHI2bzFheEl4UldrcGNINW1LbnhnXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=OWNlMjY2NDgzOGFhYzljMmVlODIwNTEwZDM4MmY4ZDNfMkhFSEdmRGFTUE9OcGxuNWREYnUySU9UVHdYa0ptd3VfVG9rZW46QlZTbWJpa0VTb1Rlbm94bm9lTGNRY2ZPbmNlXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=ZTAzNTBhMzU5N2ZjNDk4NTc1YTlmMjI2ODkyMzJlNDNfcnF0endYNWc4QjZmbUlYYU5ZaXVsbnR5c3IwODJLREhfVG9rZW46Vng0amJWUURLbzl2a3d4YXg3WmM2eWtobkxkXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

## Qwen3-VL-235B-Instruct

|      | 炉号是否能识别 | 化学/机械范围是否正确                                        | 冲击功                                                       |
| ---- | -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| VDV  | √              | √                                                            | √3次分别测试/平均数值抓的出，范围完全没问题，还推测出了材料类型 |
| 轩诺 | √              | √*（delta Fe识别出数值了，但识别为Fe）                       | √                                                            |
| 巨力 | √              | ×（识别错误力学性能要求和数值，我认为可能是合并单元格的问题） | √（抓得出平均值，也看得出三个试棒的分别测试值）              |
| 博坦 | √              | √*（S元素范围有问题，我觉得可能是引用原标准）                | 没要求                                                       |

### 轩诺

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=MjQzN2ZlMmMyODhlM2YyMGJkNDJhN2IyNTBmZmRlOGRfemF2TUhXRDVuQk5qaHlCYXB2Q2ZIZlRQNkx3UUFlQ2ZfVG9rZW46T3J0VmJyR2Zjb3lyVG94VGwxZ2NBTGl3bjliXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 巨力

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=MGY1MTlkNGU4ZTY3NDVkZWY2Y2ZlMzllNWE4OWQ2MmRfSHczRTQxY3NyalgySG1WNDJCYm9Ud2F1dUN3REdWVnpfVG9rZW46SFd6NGJnRWFxb3ZyeDB4c2wzZmMzU0o5bnBjXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 博坦

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NTc0NzA4ODMyZWUzMTQ4NDYwNjE1ZjRhZjk3NzJlMzlfR2pEdTBRenE0VzJRdWJUY0c5YWlSSzN3b0hXd21XVXFfVG9rZW46Sm5hMmIxR21VbzVaakt4ZW5SRWMyelBPbmViXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

## Qwen3-VL-32B-Instruct

|          | 炉号是否能识别 | 化学/机械范围是否正确                                        | 冲击功                                                       |
| -------- | -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| VDV      | √              | √                                                            | √（3次分别测试/平均数值抓的出，范围完全没问题，还推测出了材料类型） |
| 迪宝     | √              | √                                                            | √（3次分别测试/平均数值抓的出，范围完全没问题）              |
| 轩诺     | √              | √*（delta Fe含量没认出来，把δ识别为8了）                     | √                                                            |
| 巨力     | √              | ×（力学性能范围和数值识别错误，我感觉它是搜集了原标准的要求，没识别到文件里的要求） | √（抓得出平均值，也看得出三个试棒的分别测试值）              |
| 中山高纬 | √              | √                                                            | 没要求                                                       |
| R470     | √              | √                                                            | √                                                            |
| 博坦     | √              | √*（S元素范围有问题）                                        | 没要求                                                       |

### 轩诺

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NGY1MzU1MzRkMmIzYTZmZGUyZjJlY2Q3ZmFmMDc1MTdfUjFNOFJrYjBScjlDMWZZUkQyOUxyWjJ4OWVDNjcwZjJfVG9rZW46V2lWcmJoZWJqb2dTUml4ZTF0bGNlalBpbkRlXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 巨力

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=NzY0MWMzN2RjMjZlN2Y5YTc0ODA2ODBmNDY3NmJmMmZfOFV4UkxOU0xGbml2UWljV01xWmltYnBQWklJeDY4TTVfVG9rZW46Q1pKWGIwVHRqb2JrV3R4c0lDTmNlZmoxbndkXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=OTU4NmFlNDg3MjNmYWQ0ODcyNTZjOWI3MDBjNWJmODJfd01KS29lWUdNNzdXRHJlcUZSdmhsbjUxUmY5Y05qalJfVG9rZW46TlNKbmJIY3dibzljTGJ4Y0VzSGM5aGJjbk1iXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)

### 博坦

![img](https://wacz3jwwsbn.feishu.cn/space/api/box/stream/download/asynccode/?code=OTU3MmM0ZmE3ZTUxNzZhZGVkNzY0ODU2MWVmZmE1MzBfVTdCY1pFQVZuSTRHQ3J6YjhDbFJoZkJ2NzdSamhqMzlfVG9rZW46QlVxNGJQTVRab2pOWEF4dVI4MGN0MjhSbm5kXzE3ODAzMTgyNzY6MTc4MDMyMTg3Nl9WNA)