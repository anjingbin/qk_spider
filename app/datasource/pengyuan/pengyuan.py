# -*- coding: utf-8 -*-
import copy
import inspect
import logging
import os
import os.path
import queue
import threading
from datetime import timedelta, datetime
from optparse import OptionParser

import jpype
import time

import xmltodict
from lxml import etree
from suds.client import Client

from app.datasource.third import Third
from app.datasource.utils.tools import params_to_dict
from app.util.logger import logger
from ..configuration import config
from ..utils.tools import convert_dict
from ...util.jvm import start_jvm


class PengYuan(Third):
    """
     获取鹏元数据工具类
    """
    params_mapping = {
        'user_name_cn': 'name',
        'personal_id': 'documentNo',
        'query_reason_id': 'queryReasonID',
        'card_id': 'cardNos',
        'begin_date': 'beginDate',
        'end_date': 'endDate',
        'open_bank_id': 'openBankNo',
        'mobile_num': 'mobile',
}

    py_config = config.get('pengyuan')
    url = py_config.get('url')
    user_name = py_config.get('user_name')
    password = py_config.get('password')
    source = py_config.get('source')

    def __init__(self):
        self.client = Client(PengYuan.url)
        pass

    def create_query_condition(self, query_code, **kwargs):
        """
        生成查询条件,如果没有给定kwargs值, 该函数必须在query_内调用,根据外层函数参数自动生成查询条件
        :return:
        """
        if not len(kwargs):
            kwargs = params_to_dict(2)
        result = self.__params_dict_condition(query_code, **kwargs)
        return result

    def __params_dict_condition(self, query_code, **kwargs):
        """
        将字典转换为xml的查询条件
        :param query_code:
        :param kwargs:
        :return:
        """
        query_template = '<?xml version="1.0" encoding="GBK"?>' \
                         '<conditions>' \
                         '<condition queryType="{}">' \
                         '</condition>' \
                         '</conditions>'.format(query_code).encode()
        query_t = self.__to_xml(query_template)
        condition_reg = "//conditions/condition"
        condition = query_t.xpath(condition_reg)[0]
        for n, v in kwargs.items():
            item = etree.SubElement(condition, 'item')
            name = etree.SubElement(item, 'name')
            name.text = n
            value = etree.SubElement(item, 'value')
            value.text = v
        result = etree.tostring(query_t, encoding='unicode')
        return result

    def query(self, result, *args, **kwargs):
        """
        查询接口
        :param result:
        :param args:
        :param kwargs:
        :return:
        """
        kwargs = self.pre_query_params(*args, **kwargs)
        # TODO:子报告如何处理
        res = queue.Queue()
        threads = []
        for func in inspect.getmembers(self, predicate=inspect.ismethod):
            if func[0].startswith('query_'):
                try:
                    # 获取函数参数名,只挑选需要的参数.
                    f = func[1]
                    params = inspect.signature(f).parameters.keys()
                    ps = {param: kwargs.get(param) for param in params if kwargs.get(param) is not None}
                    thread = threading.Thread(target=self.__query_thread, args=(res, f), kwargs=ps)
                    threads.append(thread)
                    thread.start()
                except Exception as e:
                    continue

        for thread in threads:
            thread.join(5)
            if thread.isAlive():
                logger.error("查询线程{}超时".format(thread))

        result_final = []
        while True:
            try:
                data = res.get_nowait()
                if data:
                    result_final.append(data)
            except queue.Empty:
                break
        result.put((result_final, self.source))
        print(result_final)
        return result

    def __query_thread(self, result, func, **kwargs):
        """
        用于实现线程的封装查询
        :param result:
        :param func:
        :param kwargs:
        :return:
        """
        try:
            r = func(**kwargs)
            result.put(r)
        except Exception as ex:
            logger.error(ex)

    def __query(self, condition, *args, **kwargs):
        """
        根据条件申请查询
        :param condition: 查询条件
        :return: 查询结果,返回查询到的值
        """
        self.client.set_options(port='WebServiceSingleQuery')
        # TODO: 测试时不调用
        bz_result = self.client.service.queryReport(self.user_name, self.password, condition, 'xml') .encode('utf-8').strip()
        # bz_result = b'<result>\r\n\t<status>1</status>\r\n\t<returnValue>UEsDBBQACAAIADZxXEkAAAAAAAAAAAAAAAALAAAAcmVwb3J0cy54bWx9U09rE0EcPVfwOwxzaqF1d7ZJG8tkC8YqRayQ1A+w3UybJclMurMb\nG79Nkx4UC2pFYv+o+KeYEGi2SCKI1YMHESnqRQ9CcXZ2k9pkcQ+7M29n3vu995vBs2vFAigTm1uMJiG6oEJAqMmyFl1JwquXrkEwq58/h02L\np0mJ2Q4HYMlwFlgSaiqaQqo2jRKq/8QhcKnlLBhFkoRvNp8/rt1ptndqtbtPfzTee/vtav3k4Od2s3701mt/3L7XegYBd5du2CuG0D34/WCr\ncbx3cujVq13Pew3Bqkvsyk1O7PnLSbiav8UlEOIp5lJHVAuBTUxilcmi5av2KgIoMaMmZmIJeKZ0sdj/+ITDtS+5ViE7R7OnTBNInehzxWOh\ndJoYnFGfA6lIWgjIFyslwn1wSo2No5imiiAdmxhOmnC3IIpVx9XB5ZmcGKWMkhNkv15tHtePGu3uxqikGQPaevXJr0ar/qXd2f387oOf4qjk\nHgMQ5AyeqXCHFOdsm9lJuGwUOIHA4ldsdpvQHiAiGMFhajRr+Vrcx0awJfbK0Qimomu6/8KKHAaoGZSmP9zd+np4v/PJ67z6g5UeGqwpGwWX\n6K3vL6qPNrESzCS70qcfEsoy0y0SKk7Rf+W6G3snO/svv0VLaiJ/FEMXE9Mq0uJIm9Si5bEybB6XWMEySSpHzLw2T5fZ2cYEbZwcaFeKcSds\n8EBrNXFn/B5cJ5wbK2J7EPppANJkL6O+Y3yaQ6Sbf37L5baU0yexEo4kWsoxh+lYCb7ScCgssAGb0rq464ymLZ7POIYTaT44vVHmI851pHkh\nPSQj4f5lPDvj+l9QSwcINagM0moCAACJBAAAUEsBAhQAFAAIAAgANnFcSTWoDNJqAgAAiQQAAAsAAAAAAAAAAAAAAAAAAAAAAHJlcG9ydHMu\neG1sUEsFBgAAAAABAAEAOQAAAKMCAAAAAA==</returnValue>\r\n</result>'
        # print(bz_result)
        result = self.__format_result(bz_result)
        return result

    @staticmethod
    def __to_xml(bz_result):
        """
        将查询的字符串转换为xml结点
        :param bz_result:
        :return:
        """
        try:
            xml_data = etree.fromstring(bz_result)
            return xml_data
        except ValueError as e:
            logging.error("结果转换xml失败{}!", e)

    @staticmethod
    def __get_result_code(xml_result):
        """
        获取结果中的结果代码
        :param xml_result:
        :return:
        """
        code = xml_result.find('status').text
        return int(code)

    def __format_result(self, bz_result):
        """
        格式化查询结果的原始数据
        :param bz_result:
        :return:
        """
        xml_result = self.__to_xml(bz_result)
        if self.__get_result_code(xml_result) != 1:
            err_code = xml_result.find('errorCode').text
            err_message = xml_result.find('errorMessage').text
            log = u"查询异常!异常代码:{}, 错误信息:{}".format(err_code, err_message)
            logging.error(log)
            return
        rv = self.__get_result_value(xml_result)
        return rv

    def __get_result_value(self, xml_result):
        """
        获取结果中处理过的值
        :param bz_result:
        :return:
        """
        data = xml_result.find('returnValue').text
        rv = self.__format_result_value(data)
        rv = xmltodict.parse(rv,  dict_constructor=dict, xml_attribs=False)
        return rv

    def __format_result_value(self, data):
        """
        对查询到结果结果进行解码
        :return:
        """
        try:
            start_jvm()
            z_result = self.__base64_decode(data)
            rv = self.__unzip(z_result)
            return rv
        except Exception as ex:
            logger.error(ex)

    @staticmethod
    def __base64_decode(data):
        """
        鹏元元的base64解码
        :param data: resultValue原始字段内容
        :return: 解码后的内容
        """
        try:
            Base64 = jpype.JPackage('cardpay').pengyuan.Base64
            b64 = Base64()
            z_result = b64.decode(data)
            return z_result
        except Exception as ex:
            logger.error(ex)

    @staticmethod
    def __unzip(z_result):
        """
        鹏元的解压缩
        :param z_result: 未解压缩的内容
        :return: 解压缩后的内容
        """
        try:
            Cs = jpype.JPackage('cardpay').pengyuan.CompressStringUtil
            rv = Cs.decompress(z_result)
            return rv
        except Exception as ex:
            logger.error(ex)

    def query_personal_id_risk(self, name, documentNo, subreportIDs='10604', queryReasonID='101', refID=None):
        """
        个人身份认证信息/风险信息查询
        :param name: 姓名
        :param documentNo: 身份证号
        :param subreportIDs: 子查询
        :param queryReasonID: 查询原因
        :param refID: 引用ID
        :return: 查询结果
        """
        return self.__query(self.create_query_condition(25160))

    def query_card_pay_record(self, name, cardNos, beginDate=None, endDate=None,
                              subreportIDs='14506', queryReasonID='101', documentNo=None, refID=None):
        """
        卡多笔交易记录验请求xml规范
        :param name:
        :param cardNos:
        :param beginDate:
        :param endDate:
        :param subreportIDs:
        :param queryReasonID:
        :param documentNo:
        :param refID:
        :return:
        """
        kwargs = {}
        if beginDate is None and endDate is None:
            kwargs = params_to_dict(1)
            current_date = datetime.now().strftime('%Y-%m-%d')
            d_time = timedelta(days=300)
            one_year_ago = (datetime.now() - d_time).strftime('%Y-%m-%d')
            kwargs['beginDate'] = one_year_ago
            kwargs['endDate'] = current_date

        return self.__query(self.create_query_condition(25199, **kwargs))

    def query_career_capacity(self, name, documentNo, subreportIDs='13400', queryReasonID='101', refID=None):
        """
        职业资格查询接口文档
        :param name:
        :param documentNo:
        :param subreportIDs:
        :param queryReasonID:
        :param refID:
        :return:
        """
        return self.__query(self.create_query_condition(25121))

    def query_personal_enterprise_telephone(self, mobile, subreportIDs='21615',
                                            queryReasonID='101', ownerName=None, refID=None):
        """
        个人和企业信息查询
        :param mobile:
        :param subreportIDs:
        :param queryReasonID:
        :param ownerName:
        :param refID:
        :return:
        """
        return self.__query(self.create_query_condition(25128))

    def query_personal_revenue_assess(self, name, documentNo, corpName, positionName, subreportIDs=14003,
                                      queryReasonID='101', topDegree=None, graduateYear=None,
                                      college=None, fullTime=None, refID=None):
        """
        个人收入测评
        :param name:
        :param documentNo:
        :param corpName:
        :param positionName:
        :param subreportIDs:
        :param queryReasonID:
        :param topDegree:
        :param graduateYear:
        :param college:
        :param fullTime:
        :param refID:
        :return:
        """
        return self.__query(self.create_query_condition(25180))

    def query_airplane_info(self, name, documentNo=None, passport=None, month='12', subreportIDs='14100',
                            queryReasonID='101', refID=None):
        """
        航空出行信息
        :param name:
        :param documentNo:
        :param passport:
        :param month:
        :param subreportIDs:
        :param queryReasonID:
        :param refID:
        :return:
        """
        return self.__query(self.create_query_condition(25175))

    def query_personal_enterprise_risk(self, name, subreportIDs='14200', queryReasonID='101', refID=None):
        """
        个人与企业风险汇总信息
        :param name:
        :param subreportIDs:
        :param queryReasonID:
        :param refID:
        :return:
        """
        return self.__query(self.create_query_condition(25136))

    def query_personal_bank_info(self, name, documentNo, accountNo, mobile,
                                 openBankNo=None, subreportIDs='14506', queryReasonID='101', refID=None):
        """
        查询个人银行账户核查信息
        :param name:
        :param documentNo:
        :param accountNo:
        :param openBankNo:
        :param mobile:
        :param subreportIDs:
        :param queryReasonID:
        :param refID:
        :return:
        """
        return self.__query(self.create_query_condition(25173))

    def query_open_bank_info(self, accountNo, subreportIDs='14154', queryReasonID='101', refID=None):
        """
        开户行信息查询
        :param accountNo:
        :param subreportIDs:
        :param queryReasonID:
        :param refID:
        :return:
        """
        return self.__query(self.create_query_condition(25193))

    def query_personal_last_two_years_info(self, name, documentNo, subreportIDs='19901', queryReasonID='101', refID=None):
        """
        个人近两年查询记录
        :param name:
        :param documentNo:
        :param subreportIDs:
        :param queryReasonID:
        :param refID:
        :return:
        """
        return self.__query(self.create_query_condition(25136))

    def query_enterprise_last_one_year(self, corpName, subreportIDs='', queryReasonID='101', refID=None):
        """
        企业近一年查询记录,
        :param corpName:
        :param subreportIDs:
        :param queryReasonID:
        :param refID:
        :return:
        """
        # TODO:这个接口没有文档
        return self.__query(self.create_query_condition(1234))

    def query_enterprise_operation(self, corpName, registerNo, subreportIDs='22300', queryReasonID='101', refID=None):
        """
        企业经营指数
        :param corpName: 被查询企业名称
        :param registerNo: 被查询工商注册号
        :param subreportIDs:
        :param queryReasonID:
        :param refID:
        :return:
        """
        return self.__query(self.create_query_condition(25123))

    def query_trade_company_reprot(self, corpName, queryMonth, subreportIDs='', queryReasonID='101', refID=None):
        """
        商户经营分析
        :param corpName:
        :param queryMonth:
        :param subreportIDs:
        :param queryReasonID:
        :param refID:
        :return:
        """
        # TODO:这个接口有问题
        pass

    def ids_verify(self):
        """
        IDS核身产品
        :return:
        """
        # TODO:这个接口很复杂,先放下
        pass

    def query_risk_info(self):
        """
        风险信息监控接口
        :return:
        """
        pass

    def query_enterprise_info(self, corpName, orgCode, registerNo,
                              subreportIDs='21301, 21611, 21612, 22101, 22102, 22103, 22014, 22015, 22302',
                              queryReasonID='101', refID=None):
        """
        企业信息查询
        :return:
        """
        return self.__query(self.create_query_condition(25123))

    def query_car_info(self, name, documentNo, licenseNo, carType,
                       subreportIDs='13812, 13814', queryReasonID='101', refID=None):
        """
        全国车辆信息核查
        :param name:
        :param documentNo:
        :param licenseNo:
        :param carType:
        :param queryReasonID:
        :param subreportIDs:
        :param refID:
        :return:
        """
        return self.__query(self.create_query_condition(25200))

    def query_mini_loan_rish_grade(self, name, documentNo, applyMoney, applyPeriod,
                                   returnAmountBank, returnAmountLoan, contact, emersencyContact):
        """
        小额贷款风险评分
        :param name:
        :param documentNo:
        :param applyMoney:
        :param applyPeriod:
        :param returnAmountBank:
        :param returnAmountLoan:
        :param contact:
        :param emersencyContact:
        :return:
        """
        return self.__query(self.create_query_condition(25184))

    def query_car_and_house_property(self):
        """
        车辆售价和房产评估接口
        :return:
        """
        pass

    @staticmethod
    def format_result(xml_data):
        """
        处理查询结果,提取需要的信息
        :param xml_data: xml格式的查询结果
        :return:
        """
        # TODO: 先简单处理,之后在完善,未完成
        xml_result = etree.fromstring(xml_data)
        cisReport = xml_result.find('cisReports/cisReport')
        hasSystemError = bool(cisReport.get('hasSystemError'))
        isFrozen = bool(cisReport.get('isFrozen'))
        if hasSystemError and isFrozen:
            return

        result = {}
        for item in cisReport.items():
            if item.tag == 'queryConditions':
                continue
            item_dict = {}
            if item.get('treatResult') == '1':
                item_dict1 = {}
                for item1 in item.items():
                    if item1.tag == 'item':
                        pass

    def create_file(self, condition, result, query_type, *args):
        """
        该函数废弃
        :param condition:
        :param result:
        :param query_type:
        :param args:
        :return:
        """
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        file_dir = basedir + '/result/' + str(query_type) + '/'
        if not os.path.exists(file_dir):
            os.mkdirs(file_dir)
        file_path = file_dir + str(condition.get('documentNo'))
        for ar in args:
            file_in = file_path + ar
            file_out = file_path + ar
        file_in += '_in.xml'
        file_out += '_out.xml'

        if result is not None:
            with open(file_in, 'wb') as fi:
                fi.write(condition.encode('utf-8'))

            with open(file_out, 'wb') as fo:
                fo.write(result.encode('utf-8'))


if __name__ == '__main__':
    # py = PengYuan()
    # py.test_query_personal_id_risk(name=u'阎伟晨', documentNo='610102199407201510')
    pass


