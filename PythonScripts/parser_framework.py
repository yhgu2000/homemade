################################################################################
#
# 版权所有 (c) 2019 顾宇浩。保留所有权利。
#
# 文件: parser_framework.py
# 说明：这是我所有python指令脚本的参数解析框架
# 版本: v1.0 (2019-12-1)
#
################################################################################
#
#
class InvalidOption(Exception):
    def __init__(self,msg:str):
        Exception.__init__(self,msg)
        return


class InvalidArgument(Exception):
    def __init__(self,msg:str):
        Exception.__init__(self,msg)
        return


class MissingArgument(Exception):
    def __init__(self,msg:str):
        Exception.__init__(self,msg)
        return


class UnexpectedArgument(Exception):
    def __init__(self,msg:str):
        Exception.__init__(self,msg)
        return


class Option(object):
    """选项参数类
    """
    @staticmethod
    def default_checker_no_arguments(extra_args):
        """默认检查参数

        适用于无附加参数的选项检查。
        """
        if len(extra_args):
            raise UnexpectedArgument(extra_args[0])
        return

    def __init__(self,priority:int,executer,
                 checker=default_checker_no_arguments.__func__):
        """
        参数：
            priority:   优先级
                越小越优先。
                一次指令只会执行一个优先级非0的选项。
                所以，将诸如'-r'类的环境参数定义为0，将'--auto'类的动作参数定义为
                非零数。
                将诸如'--help'类的参数定义为负数，以获得最高优先级。
                如果一次指令没有非零选项，则会执行默认动作参数。

            executer:   执行函数
                此函数要求接受一个参数：
                    第一个参数是一个list，为此选项的附加静态参数序列。
                函数示例：
                    def executer(args):
                        pass

            checker:    语法检查函数（可选）
                预检查附加静态参数。
                此函数要求接受一个参数：
                    第一个参数是一个list，为此动作的附加静态参数序列。
                在此函数内进行参数数目等检查，抛出三大异常表示失败，不抛出异常
                视为通过检查。

        返回:
            无

        异常：
            无
        """
        self.priority = priority
        self.checker = checker
        self.executer = executer
        return
    

class Parser:
    """解析器类

    此类为对指令参数解析器的抽象。
    
    在按要求初始化之后，请按如下流程处理一条指令：
        调用parse解析指令列表
        调用check检查指令合法性（可选）
        调用execute执行指令列表

    调用auto_process或使用重载的调用运算符自动进行流程，并处理所有相关异常
    """
    @staticmethod
    def default_invalid_option_proc(key_info):
        """默认无效选项处理函数
        """
        return


    def __init__(self,
                 option_map:dict,
                 zero_checker,
                 zero_executer,
                 default_execute_option:Option,
                 blank_arguments_proc):
        """
        参数：
            movement_map:   指令映射
                键必须为以'-'开头的str，值为Option类型。

            zero_checker:   零位检查函数
                函数必须接受一个参数：
                    第一个参数是一个list，为零位参数序列。
                解析器将在所有其他参数检查之前首先检查零位参数。

            zero_executer:  零位执行函数
                函数必须接受一个参数：
                    第一个参数是一个list，为零位参数序列。
                解析器将会在所有动作选项执行之前首先执行此函数。

            default_execute_option: 用户没有指定动作选项时的默认动作选项

            blank_arguments_proc:   不带任何参数时调用的处理函数
                与default_option区别在于，在用户没有给出任何参数（包括零位参数）
                时，才会调用此函数。

        返回:
            无

        异常：
            无
        """
        self.option_map = option_map
        self.zero_checker = zero_checker
        self.zero_executer = zero_executer
        self.default_execute_option = default_execute_option
        self.blank_arguments_proc = blank_arguments_proc
        self.zero_args = []  # 零位参数（存放第一个动作参数之前的参数）
        self.option_block_list = []  # 选项块列表
        return


    def parse(self,sys_argv:list):
        """解析参数列表

        解析参数列表以初始化self.zero_argv与self.arg_block_list。
        在处理一次指令时首先调用此函数传入参数串。

        参数：
            sys_argv:   系统传入参数，即sys.argv

        返回:
            无

        异常：
            无        
        """
        sys_argv_iter = iter(sys_argv)
        option_block = (None,self.zero_args)
        while True:
            try:
                arg = next(sys_argv_iter)
                if arg.startswith('-'):
                    option_block = (self.option_map[arg],[])
                    self.option_block_list.append(option_block)
                else:
                    option_block[1].append(arg)
            except StopIteration:
                break
            except KeyError:
                raise InvalidOption(arg)
        # 对arg_block_list按优先级排序
        self.option_block_list.sort(key=lambda arg_block:arg_block[0].priority)
        return


    def check(self):
        """进行语法检查

        参数：
            无

        返回:
            无

        异常：
            取决于注册的Option类的checker函数
        """
        self.zero_checker(self.zero_args)
        for option,extra_args in self.option_block_list:
            option.checker(extra_args)
        return


    def execute(self):
        """执行动作列表

        参数：
            无

        返回:
            无

        异常：
            取决于注册的Option类的checker函数
        """
        # 首先检查是否是空指令
        if len(self.option_block_list) == 0 and len(self.zero_args) <= 1:
            self.blank_arguments_proc()
            return
        # 不是空指令则执行
        self.zero_executer(self.zero_args)
        for option,extra_args in self.option_block_list:
            # 若是动作参数则执行完立即结束运行
            if option.priority:
                option.executer(extra_args)
                return
            # 否则是环境参数，配置环境参数
            option.executer(extra_args)
        # 如果for循环结束则说明没有动作参数，执行默认动作参数
        self.default_execute_option.executer([])
        return


    def auto_process(self,sys_argv:list):
        """自动解析、检查、执行并且处理异常

        参数：
            sys_argv:   系统传入参数，即sys.argv

        返回:
            无

        异常：
            不会产生参数相关异常
        """
        try:
            self.parse(sys_argv)
            self.check()
            self.execute()
        except InvalidOption as err:
            print("invalid option -- '",err.args[0],"'",sep="")
        except InvalidArgument as err:
            print("InvalidArgument:",err.args[0])
        except MissingArgument as err:
            print("MissingArgument:",err.args[0])
        except UnexpectedArgument as err:
            print("UnexpectedArgument:",err.args[0])
        return


    def clear(self):
        """清理上一次的指令解析数据

        参数：
            无

        返回:
            无

        异常：
            无        
        """
        self.zero_args = []
        self.option_block_list = []
        return


    def __call__(self,sys_argv:list):
        """自动解析、检查、执行并且处理异常

        即调用self.auto_process函数。

        参数：
            无

        返回:
            无

        异常：
            不会产生参数相关异常
        """
        return self.auto_process(sys_argv)


def main():
    """模块测试主函数
    """
    def zero_check(zero_args):
        print("zero_args checked")
        return

    def zero_execute(zero_args):
        print("zero_args:",zero_args)
        return

    def help_proc(args):
        print("help_proc executed")
        return
    
    def read_proc(args):
        print(a)
        return

    def write_check(args):
        if len(args) != 1:
            raise MissingArgument("write check needs 1 extra arguments")
        return

    def write_proc(extra_args):
        nonlocal a
        a = extra_args[0]
        return

    def blank_proc():
        print("blank_proc executed")
        return

    a = "a is not inited"
    option_map = {"--help":Option(-1,help_proc),
                  "-r":Option(1,read_proc),
                  "-w":Option(0,write_proc,write_check)}
    p = Parser(option_map,zero_check,zero_execute,option_map['-r'],blank_proc)
    while(True):
        p(input().split())
        p.clear()
    return


if __name__ == "__main__":
    main()
